# -*- coding: utf-8 -*-
import os, glob, cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    matthews_corrcoef,
)
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    GlobalAveragePooling2D,
    Dense,
    Dropout,
)
from tensorflow.keras.applications import VGG19
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import collections

size = 224  # VGG19 standard input size
inputShape = (size, size, 3)  # RGB input for VGG19

def load_images(paths):
    images = []
    for p in paths:
        for f in glob.glob(p):
            img = cv2.imread(f, 0)  # Read as grayscale
            if img is not None:
                img = cv2.resize(img, (size, size))
                # Convert grayscale to RGB by repeating channels
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                images.append(img)
    return np.asarray(images)

# File paths
train_pothole = ["My Dataset/train/Pothole/*.jpg"]
train_plain = ["My Dataset/train/Plain/*.jpg"]
test_pothole = ["My Dataset/test/Pothole/*.jpg"]
test_plain = ["My Dataset/test/Plain/*.jpg"]

# Load image arrays once to avoid duplicated work
train_pothole_imgs = load_images(train_pothole)
train_plain_imgs = load_images(train_plain)
test_pothole_imgs = load_images(test_pothole)
test_plain_imgs = load_images(test_plain)

# Load and label data
X_train = np.concatenate((train_pothole_imgs, train_plain_imgs), axis=0)
y_train = np.concatenate(
    (np.ones(len(train_pothole_imgs)), np.zeros(len(train_plain_imgs)))
)
X_test = np.concatenate((test_pothole_imgs, test_plain_imgs), axis=0)
y_test = np.concatenate(
    (np.ones(len(test_pothole_imgs)), np.zeros(len(test_plain_imgs)))
)

# Shuffle
dx, dy = shuffle(X_train, y_train, random_state=42)
X_train, y_train = dx, dy

dx, dy = shuffle(X_test, y_test, random_state=42)
X_test, y_test = dx, dy

# Normalize and encode (already in RGB format from load_images)
X_train = X_train.astype('float32') / 255.
X_test = X_test.astype('float32') / 255.
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

def build_model():
    """VGG19-based model with transfer learning."""
    # Load VGG19 base model with pre-trained ImageNet weights
    base_model = VGG19(
        weights='imagenet',
        include_top=False,
        input_shape=inputShape
    )
    
    # Freeze base model layers initially (can unfreeze later for fine-tuning)
    base_model.trainable = False
    
    # Build the model
    inputs = base_model.input
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation="relu", kernel_regularizer=l2(1e-4))(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation="relu", kernel_regularizer=l2(1e-4))(x)
    x = Dropout(0.5)(x)
    outputs = Dense(2, activation="softmax")(x)
    
    model = Model(inputs, outputs)
    return model

model = build_model()
model.compile(
    optimizer=Adam(learning_rate=5e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# Train
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(
    X_train,
    y_train,
    validation_split=0.1,
    epochs=100,
    callbacks=[early_stop]
)

# Evaluate
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test accuracy: {accuracy:.4f}")

# Predict for metrics
pred_probs = model.predict(X_test)
pred_labels = np.argmax(pred_probs, axis=1)
true_labels = np.argmax(y_test, axis=1)

# Classification report
target_names = ["Plain", "Pothole"]
print("\nClassification Report (Precision, Recall, F1-score):")
print(
    classification_report(
        true_labels, pred_labels, target_names=target_names, zero_division=0
    )
)

# F1-score summary
f1 = f1_score(true_labels, pred_labels, average=None)
for i, c in enumerate(target_names):
    print(f"F1-score for {c}: {f1[i]:.4f}")
print(f"Macro F1-score: {f1_score(true_labels, pred_labels, average='macro'):.4f}")

cm = confusion_matrix(true_labels, pred_labels)

# Binary classification metrics (treat Pothole as positive class)
precision = precision_score(true_labels, pred_labels, zero_division=0)
recall = recall_score(true_labels, pred_labels, zero_division=0)
f1_macro = f1_score(true_labels, pred_labels, average="macro")
f1_positive = f1_score(true_labels, pred_labels, average="binary", zero_division=0)
tn, fp, fn, tp = cm.ravel()
specificity = tn / (tn + fp) if (tn + fp) else 0.0
auc_score = (
    roc_auc_score(true_labels, pred_probs[:, 1]) if len(np.unique(true_labels)) > 1 else np.nan
)
mcc = matthews_corrcoef(true_labels, pred_labels)

metrics_summary = {
    "Precision": precision,
    "Recall": recall,
    "Specificity": specificity,
    "F1 Score": f1_positive,
    "AUC Score": float(auc_score) if not np.isnan(auc_score) else 0.0,
    "MCC Score": mcc,
}

print("\nAggregated Metrics:")
for k, v in metrics_summary.items():
    print(f"{k}: {v:.4f}")
print(f"Macro F1-score: {f1_macro:.4f}")

# Save the model
model.save('pothole_model.h5')

SUMMARY_DIR = "artifacts"
SUMMARY_IMAGE = os.path.join(SUMMARY_DIR, "training_summary.png")


def plot_training_summary(history_obj, confusion_mtx, metrics_dict, class_names):
    """Create a single image summarizing training, confusion matrix, and key metrics."""
    history_data = history_obj.history
    train_acc = history_data.get("accuracy", [])
    val_acc = history_data.get("val_accuracy", [])

    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1])

    # Accuracy curves
    ax_curve = fig.add_subplot(gs[0, :])
    ax_curve.plot(train_acc, label="Train Accuracy")
    ax_curve.plot(val_acc, label="Validation Accuracy")
    ax_curve.set_xlabel("Epoch")
    ax_curve.set_ylabel("Accuracy")
    ax_curve.set_title("Training vs Validation Accuracy")
    ax_curve.legend(loc="lower right")
    ax_curve.grid(alpha=0.2)

    # Confusion matrix
    ax_cm = fig.add_subplot(gs[1, 0])
    disp = ConfusionMatrixDisplay(confusion_matrix=confusion_mtx, display_labels=class_names)
    disp.plot(ax=ax_cm, cmap=plt.cm.Blues, colorbar=False)
    ax_cm.set_title("Confusion Matrix")

    # Metrics bar chart + table stacked on right
    right_gs = gs[1, 1].subgridspec(2, 1, height_ratios=[3, 1])
    ax_metrics = fig.add_subplot(right_gs[0, 0])
    metric_names = list(metrics_dict.keys())
    metric_values = [metrics_dict[name] for name in metric_names]
    x_pos = np.arange(len(metric_names))
    bars = ax_metrics.bar(x_pos, metric_values, color="#4c72b0")
    ax_metrics.set_ylim(0, 1)
    ax_metrics.set_ylabel("Score")
    ax_metrics.set_title("Key Evaluation Metrics")
    ax_metrics.set_xticks(x_pos)
    ax_metrics.set_xticklabels(metric_names, rotation=45, ha="right")
    for bar, value in zip(bars, metric_values):
        ax_metrics.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # Metrics table
    ax_table = fig.add_subplot(right_gs[1, 0])
    ax_table.axis("off")
    cell_text = [[name, f"{metrics_dict[name]:.3f}"] for name in metric_names]
    table = ax_table.table(
        cellText=cell_text,
        colLabels=["Metric", "Score"],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.4)
    ax_table.set_title("Metric Values", pad=10)

    fig.suptitle("Pothole Detection Training Summary (VGG19)", fontsize=16)
    fig.tight_layout()
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    fig.savefig(SUMMARY_IMAGE, dpi=200, bbox_inches="tight")
    plt.show()


plot_training_summary(history, cm, metrics_summary, target_names)
