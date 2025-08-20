document.querySelector('.collapse-icon').addEventListener('click', () => {
    document.querySelector('.side-bar').classList.toggle('active');
  });
    document.querySelector('.uncollapse-icon').addEventListener('click', () => {
    document.querySelector('.side-bar').classList.toggle('active');
  });



const steps = document.querySelectorAll(".form-step");
const progressSteps = document.querySelectorAll(".progressbar .step");
const nextBtns = document.querySelectorAll(".next-btn");
const prevBtns = document.querySelectorAll(".prev-btn");
let currentStep = 0;

function updateStepDisplay() {
steps.forEach((step, index) => {
    step.classList.toggle("active", index === currentStep);
});
progressSteps.forEach((step, index) => {
    step.classList.toggle("active", index === currentStep);
});
}

nextBtns.forEach(btn => {
btn.addEventListener("click", () => {
    if (currentStep < steps.length - 1) {
    currentStep++;
    updateStepDisplay();
    }
});
});

prevBtns.forEach(btn => {
btn.addEventListener("click", () => {
    if (currentStep > 0) {
    currentStep--;
    updateStepDisplay();
    }
});
});
progressSteps.forEach((step, index) => {
    step.addEventListener("click", () => {
      currentStep = index;
      updateStepDisplay();
    });
  });

// Initialize on load
updateStepDisplay();

let formFields = [
  {label: "First Name" , name: "firstname", category : "Profile Info", required: true, value : ""},
  {label: "Last Name" , name: "lastname", category : "Profile Info", required: true, value : ""},
  {label : "Gender", name: "gender", category: "Profile Info", required: true, value : ""},
  {label: "Marital Status", name: "maritalstatus", category: "Profile Info", required: true, value : ""},
  {label: "Date of Birth", name: "dateofbirth", category: "Profile Info", required: true, value : ""},
  {label: "Place of Birth", name: "placeofbirth", category: "Profile Info", required: true, value : ""},
  {label: "ID Card Number", name: "idcardnumber", category: "Profile Info", required: true, value : ""},
  {label: "Date of Issue", name: "dateofissue", category: "Profile Info", required: true, value : ""},
  {label: "Date of Expiry", name: "dateofexpiry", category: "Profile Info", required: true, value : ""},
  {label: "CNIC Front", name: "cnicfront", category: "Profile Info", required: true, type: "file", value : ""},
  {label: "CNIC Back", name: "cnicback", category: "Profile Info", required: true, type: "file", value : ""},
  {label: "Email", name: "email", category: "Contact Info", required: true, type: "email", value : ""},
  {label: "Phone Number", name: "phonenumber", category: "Contact Info", required: true, type: "tel", value : ""},
  {label: "PTA", name: "pta", category: "Contact Info", required: false, type: "checkbox", value : ""},
  {label: "Mailing Address", name: "mailingaddress", category: "Contact Info", required: true, value : ""},
  {label: "Add", name: "add", category: "Contact Info", required: false, type: "checkbox", value : ""},
  {label: "Bank Name", name: "bankname", category: "Bank Info", required: true, value : ""},
  {label: "IBAN", name: "iban", category: "Bank Info", required: true, value : ""},
  {label: "Proof of IBAN", name: "proofiban", category: "Bank Info", required: true, type: "file", value : ""},
  {label: "Employment", name: "employment", category: "Employment Info", required: true, value : ""},
  {label: "Zakat", name: "zakat", category: "Zakat and Signature", required: false, type: "checkbox", value : ""},
  {label: "Digital Signature", name: "digitalsignature", category: "Zakat and Signature", required: true, type: "file", value : ""},
  {label: "Nominee Name", name: "nom-name", category: "Nominee Info", required: true, value : ""},
  {label: "Nominee ID", name: "nom-id", category: "Nominee Info", required: true, value : ""},
  {label: "Nominee ID Front", name: "nom-id-front", category: "Nominee Info", required: true, type: "file", value : ""},
  {label: "Nominee ID Back", name: "nom-id-back", category: "Nominee Info", required: true, type: "file", value : ""},
  {label: "Nominee ID Expiry Date", name: "nom-id-exp-date", category: "Nominee Info", required: true, value : ""},
  {label: "Nominee ID Expiry", name: "nom-id-exp", category: "Nominee Info", required: false, type: "checkbox", value : ""},
  {label: "Relation with Nominee", name: "Relation-w-nominee", category: "Nominee Info", required: true, value : ""},
  {label: "Nominee Proof", name: "nom-proof", category: "Nominee Info", required: true, type: "file", value : ""},
  {label: "UKN", name: "ukn", category: "UKN Info", required: true, value : ""},
  {label: "Proof of UKN", name: "proof-ukn", category: "UKN Info", required: true, type: "file", value : ""}
];


document.querySelectorAll('.next-btn').forEach(button => {
  document.addEventListener('click', ()=>{

    const formStep = button.closest('.form-step');
    const inputs = formStep.querySelectorAll("input, select, textarea");
    inputs.forEach(input => {
      console.log(input.value);
        formFields.forEach(field => {
          if(input.name === field.name){
            field.value = input.value;
          }
        })
        console.log(formFields)
        // console.log("Form fields being sent:", formFields); // Add this

        fetch("/user-details/submit-form", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ formFields }),
        })
        .then((res) => res.json())
        .then((data) => {
          console.log("Success:", data);
        })
        .catch((err) => {
          console.error("Error submitting form:", err);
        });

    })
  })
})


const review_container = document.querySelector('.review-container');

// Step 1: Group fields by category
const groupedFields = {};
formFields.forEach(field => {
  if (!groupedFields[field.category]) {
    groupedFields[field.category] = [];
  }
  groupedFields[field.category].push(field);
});

// Step 2: Render each category and its fields
for (const category in groupedFields) {
  const categorySection = document.createElement('div');
  categorySection.classList.add('category-section');

  // Add heading
  const heading = document.createElement('h3');
  heading.textContent = category;
  categorySection.appendChild(heading);

  // Add each field under this category
  groupedFields[category].forEach(field => {
    const wrapper = document.createElement('div');
    wrapper.classList.add('form-group');

    const field_review = document.createElement('div');
    field_review.classList.add('field-review');
    if (field.required) {
      field_review.classList.add('required');
    }
    field_review.textContent = field.label;

    const review = document.createElement('div');
    review.classList.add('review');

    if (field.value === "") {
      review.innerHTML = `<span class="error">Not Provided</span>`;
    } else {
      review.textContent = field.value;
    }

    wrapper.appendChild(field_review);
    wrapper.appendChild(review);
    categorySection.appendChild(wrapper);
  });

  // Add this entire category section to the main container
  review_container.appendChild(categorySection);
}




