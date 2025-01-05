const sidebar = document.querySelector(".sidebar");
const toggle = document.querySelector(".sidebar-toggler");

toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
});
document.querySelector('.sidebar-toggler').addEventListener('click', function() {
  const closeButton = document.querySelector('.close');
  setTimeout(() => {
      closeButton.style.fontSize = '1rem'; // Reset font size after transition
  }, 400); // Match the sidebar's transition duration
});

let cropper;
let formChanged = false;
let originalFormData;
let originalImageDataUrl = "{{ url_for('static', filename=user.Photo) }}"; // Original image URL

// Function to save the initial state of the form
function saveInitialState() {
  console.log("Saving initial form state...");
  originalFormData = new FormData(document.getElementById('profileForm')); // Save initial form state
  originalImageDataUrl = document.getElementById('profilePicturePreview').src; // Save original profile photo
  console.log("Initial state saved:", originalFormData, originalImageDataUrl);
}

// Call this on page load to save the initial state
saveInitialState();

// Track changes in the form (text fields)
document.getElementById('profileForm').addEventListener('input', function() {
  formChanged = true;
  console.log("Form changed - input detected.");
});

// Detect changes in profile photo input
document.getElementById('profilePhotoInput').addEventListener('change', function(event) {
  formChanged = true; // Mark as changed
  console.log("Profile photo changed.");
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function(e) {
    const image = document.getElementById('imageToCrop');
    image.src = e.target.result;
    document.getElementById('cropContainer').style.display = 'block';  // Show cropping container

    console.log("Image loaded for cropping.");

    if (cropper) {
      cropper.destroy(); // Destroy previous cropper instance
      console.log("Previous cropper instance destroyed.");
    }

    cropper = new Cropper(image, {
      aspectRatio: 1,
      viewMode: 1,
    });
    console.log("Cropper initialized.");
  };

  reader.readAsDataURL(file);
});

// Save the cropped image to hidden input
document.getElementById('saveCroppedImage').addEventListener('click', function() {
  if (cropper) {
    const canvas = cropper.getCroppedCanvas();
    const croppedImageDataUrl = canvas.toDataURL('image/jpeg');
    
    // Update hidden input with cropped image
    document.getElementById('cropped_image').value = croppedImageDataUrl;
    
    // Update the profile picture preview
    document.getElementById('profilePicturePreview').src = croppedImageDataUrl;

    // Hide the crop container
    document.getElementById('cropContainer').style.display = 'none';

    console.log("Cropped image saved and preview updated.");

    cropper.destroy();
    formChanged = true; // Mark form as changed
  }
});

// Reset the form to its original state
function resetForm() {
  console.log("Resetting form to original state...");
  const form = document.getElementById('profileForm');
  const formData = new FormData(form);

  // Reset each field to its original value
  for (const [key, value] of originalFormData.entries()) {
    const field = form.querySelector(`[name=${key}]`);
    if (field) {
      field.value = value;
    }
  }

  // Reset profile picture to original one
  document.getElementById('profilePicturePreview').src = originalImageDataUrl;
  console.log("Form reset complete.");
}

// Modal close event handler
$('#settingsModal').on('hide.bs.modal', function (e) {
  console.log("Modal is about to close...");
  if (formChanged) {
    console.log("Form has unsaved changes, prompting user for confirmation...");
    const confirmClose = confirm("You have unsaved changes. Do you want to save them?");
    if (!confirmClose) {
      console.log("User chose not to save changes. Preventing modal close...");
      e.preventDefault();

      // Reset form fields to original state
      resetForm();

      // Reset change detection flag
      formChanged = false;

      // Explicitly hide modal after reset
      $('#settingsModal').modal('hide');
    } else {
      console.log("User chose to discard changes. Modal will close.");
    }
  } else {
    console.log("No unsaved changes. Modal will close normally.");
  }
});

// Reset form on modal open (when modal is shown again)
$('#settingsModal').on('show.bs.modal', function () {
  console.log("Modal opened. Resetting change detection.");
  // Reset changes if modal is being opened again
  formChanged = false;
});

// Reset form change flag after form submission
document.getElementById('profileForm').addEventListener('submit', function() {
  console.log("Form submitted. Resetting form change flag.");
  formChanged = false; // Reset form change flag after form submission
});


// JavaScript to toggle visibility of the input field
document.getElementById('showInputButton').addEventListener('click', function() {
    var formGroup = document.getElementById('linkInputGroup');
    formGroup.style.display = (formGroup.style.display === 'none' || formGroup.style.display === '') ? 'block' : 'none';
    var deleteButtons = document.querySelectorAll('.delete-link-btn');
    deleteButtons.forEach(function(button) {
        // Toggle display: If hidden, show it; if shown, hide it
        button.style.display = (button.style.display === 'none' || button.style.display === '') ? 'inline-block' : 'none';
    });
});
    // Delete a link when the - button is clicked
    document.querySelectorAll('.delete-link-btn').forEach(button => {
      button.addEventListener('click', function() {
          const index = this.getAttribute('data-index');
          const linkItem = document.getElementById('link-item-' + index);
          
          // Send AJAX request to delete the link
          fetch('/dashboard/profile/delete_link', {
              method: 'POST',
              body: JSON.stringify({ index: index }),
              headers: {
                  'Content-Type': 'application/json'
              }
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  location.reload()
              } else {
                  alert('Error deleting link.');
              }
          });
      });
    });
