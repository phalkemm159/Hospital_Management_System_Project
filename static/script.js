document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("prescriptionModal");
    const openModalBtn = document.getElementById("openPrescriptionBtn");
    const prescriptionForm = document.getElementById("prescriptionForm");
  
    if (openModalBtn) {
      openModalBtn.addEventListener("click", () => {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
      });
    }
  
    function closeModal() {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
  
    window.closeModal = closeModal;
  
    if (prescriptionForm) {
      prescriptionForm.addEventListener("submit", function (e) {
        e.preventDefault();
  
        const formData = new FormData(this);
        const newPrescription = {
          patient: formData.get("patientName"),
          medicine: formData.get("medicine"),
          dosage: formData.get("dosage"),
          instructions: formData.get("instructions")
        };
  
        fetch("/add_prescription", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(newPrescription)
        })
          .then(res => res.json())
          .then(data => {
            alert(data.message);
            closeModal();
            this.reset();
            if (!document.getElementById("prescriptionsSection").classList.contains("hidden")) {
              showPrescriptions();
            }
          });
          
      });
    }
  
    function showPrescriptions() {
      const section = document.getElementById("prescriptionsSection");
      const list = document.getElementById("prescriptionList");
  
      section.classList.remove("hidden");
      document.getElementById("appointmentsSection").classList.add("hidden");
      document.getElementById("patientsSection").classList.add("hidden");
      document.getElementById("recordsSection").classList.add("hidden");
  
      list.innerHTML = "";
  
      fetch("/get_prescriptions")
        .then(res => res.json())
        .then(prescriptions => {
          prescriptions.forEach(p => {
            const card = document.createElement("div");
            card.className = "border p-4 rounded-xl bg-gray-50";
            card.id = `prescription-${p.id}`;
            card.innerHTML = `
                <div class="flex justify-between items-start">
                    <div>
                      <p class="font-semibold text-lg">${p.patient}</p>
                      <p class="text-sm text-gray-600">Date: ${p.date}</p>
                      <p class="text-sm text-gray-700"><strong>Medicine:</strong> ${p.medicine}</p>
                      <p class="text-sm text-gray-700"><strong>Dosage:</strong> ${p.dosage}</p>
                      <p class="text-sm text-gray-700"><strong>Instructions:</strong> ${p.instructions}</p>
                    </div>
                    <button onclick="deletePrescription('${p.id}')" class="text-sm bg-red-500 text-white px-3 py-1 rounded h-fit ml-4">Delete</button>
                </div>
            `;


            list.appendChild(card);
          });
        });
    }

    window.showPrescriptions = showPrescriptions;
  
    window.showSection = function (section) {
      const sections = ['appointments', 'patients', 'records', 'prescriptions'];
      
      // Hide all sections
      sections.forEach(id => {
          const sec = document.getElementById(id + 'Section');
          if (sec) sec.classList.add('hidden');
      });
  
      // Show the selected section
      const targetSection = document.getElementById(section + 'Section');
      if (targetSection) targetSection.classList.remove('hidden');
  
      // Highlight the active tab
      const buttons = document.querySelectorAll('.tab-btn');
      buttons.forEach(btn => {
          btn.classList.remove('bg-black', 'text-white');
          btn.classList.add('bg-white', 'text-black', 'border');
      });
  
      const sectionMap = {
          appointments: "Today's Appointments",
          patients: "My Patients",
          records: "Medical Records",
          prescriptions: "Prescriptions"
      };
  
      buttons.forEach(btn => {
          if (btn.textContent.trim() === sectionMap[section]) {
              btn.classList.remove('bg-white', 'text-black', 'border');
              btn.classList.add('bg-black', 'text-white');
          }
      });
  
      // Handle special buttons visibility
      const addAppointmentBtn = document.getElementById('addAppointmentBtn');
      const openPrescriptionBtn = document.getElementById('openPrescriptionBtn');
      const addPatientBtn = document.getElementById('addPatientBtn');
      const addMedicalRecordBtn = document.getElementById('addMedicalRecordBtn');
  
      if (addAppointmentBtn) addAppointmentBtn.classList.add('hidden');
      if (openPrescriptionBtn) openPrescriptionBtn.classList.add('hidden');
      if (addPatientBtn) addPatientBtn.classList.add('hidden');
      if (addMedicalRecordBtn) addMedicalRecordBtn.classList.add('hidden');
  
      switch (section) {
          case 'appointments':
              if (addAppointmentBtn) addAppointmentBtn.classList.remove('hidden');
              break;
          case 'patients':
              if (addPatientBtn) addPatientBtn.classList.remove('hidden');
              break;
          case 'records':
              if (addMedicalRecordBtn) addMedicalRecordBtn.classList.remove('hidden');
              break;
          case 'prescriptions':
              if (openPrescriptionBtn) openPrescriptionBtn.classList.remove('hidden');
              showPrescriptions();
              break;
          default:
              break;
      }
  };
  
      
  });

  function deletePrescription(id) {
    if (confirm("Are you sure you want to delete this prescription?")) {
      fetch(`/delete_prescription/${id}`, {
        method: 'DELETE',
      })
      .then(response => {
        if (response.ok) {
            alert('Prescription deleted successfully!');
            // Remove the prescription card from the DOM
            const card = document.getElementById(`prescription-${id}`);
            if (card) {
              card.remove();
            } // ⬅️ Reload the page
        } else {
          alert('Failed to delete prescription.');
        }
      });
    }
  }
  
  
  
  const appointments = [
    { time: "10:00 AM", name: "John Doe", age: 59, type: "Follow-up", status: "Checked-in", date: "2025-04-10" },
    { time: "10:30 AM", name: "Jane Smith", age: 45, type: "Consultation", status: "Waiting", date: "2025-04-10" },
    { time: "11:45 AM", name: "Robert Johnson", age: 62, type: "Check-up", status: "Waiting", date: "2025-04-10" },
    { time: "01:00 PM", name: "Emily Davis", age: 29, type: "Check-up", status: "Check-up", date: "2025-04-10" },
    { time: "03:00 PM", name: "Michael Brown", age: 43, type: "Consultation", status: "Consultation", date: "2025-04-10" }
  ];

  const appointmentContainer = document.querySelector(".space-y-4");
  const searchInput = document.querySelector("input[placeholder='Search appointments...']");

  function renderAppointments(filter = "All", query = "") {
    appointmentContainer.innerHTML = "";
    const today = "2025-04-10"; // For demo purposes
    const filtered = appointments.filter(app => {
      const matchStatus = filter === "All" || app.status === filter;
      const matchSearch = app.name.toLowerCase().includes(query.toLowerCase());
      return matchStatus && matchSearch;
    });
    filtered.forEach(app => {
      appointmentContainer.innerHTML += `
        <div class="bg-white p-4 rounded shadow flex justify-between items-center">
          <div>
            <p class="font-bold text-lg">${app.time} - ${app.name}</p>
            <p class="text-sm text-gray-500">Age ${app.age} · App. ${app.type}</p>
          </div>
          <div class="flex gap-2">
            <span class="bg-gray-200 text-black px-2 py-1 rounded text-sm">${app.status}</span>
            <button class="bg-black text-white px-3 py-1 rounded">${app.status === 'Checked-in' ? 'View' : 'Start'}</button>
          </div>
        </div>`;
    });
  }

  // Filter buttons
  document.querySelectorAll(".flex.space-x-2.mb-4 button").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".flex.space-x-2.mb-4 button").forEach(btn => btn.classList.remove("bg-black", "text-white"));
      button.classList.add("bg-black", "text-white");
      renderAppointments(button.textContent.trim());
    });
  });

  // Search
  searchInput.addEventListener("input", () => {
    const filterBtn = document.querySelector(".flex.space-x-2.mb-4 button.bg-black").textContent.trim();
    renderAppointments(filterBtn, searchInput.value);
  });

  // Tabs (Upcoming, Today, etc.) - Just logs for now
  document.querySelectorAll(".border-b.pb-2 button").forEach(tab => {
    tab.addEventListener("click", () => {
      alert(`Filter by tab: ${tab.textContent.trim()}`);
    });
  });

  // Print Schedule
  document.querySelector("button:contains('Print Schedule')")?.addEventListener("click", () => {
    window.print();
  });

  // Add New Appointment button - example prompt
  document.querySelector("button:contains('+ New Appointment')")?.addEventListener("click", () => {
    const name = prompt("Enter patient's name:");
    if (!name) return;
    const newApp = {
      time: "02:00 PM",
      name: name,
      age: 30,
      type: "Consultation",
      status: "Waiting",
      date: "2025-04-10"
    };
    appointments.push(newApp);
    renderAppointments();
  });

  renderAppointments();

document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("prescriptionsSectionPatient")) {
    showPrescriptionsPatient();
  }
  
  
  function showPrescriptionsPatient() {
  const section = document.getElementById("prescriptionsSectionPatient");
  const list = document.getElementById("prescriptionTableBody");
  list.innerHTML = "";
  fetch("/get_prescriptions")
    .then(res => res.json())
    .then(prescriptions => {
      prescriptions.forEach(p => {
        const card = document.createElement("tbody");
        card.className = "border p-4 rounded-xl bg-gray-50";
        card.id = `prescription-${p.id}`;
        card.innerHTML = `
              <tr class="border-b">
                <td class="py-2">
                  <div class="font-medium">${p.patient}</div>
                  <div class="text-xs text-gray-500">ID: PT-${p.id}</div>
                </td>
                <td>${p.medicine}</td>
                <td>${p.date}</td>
                <td><span class="bg-black text-white text-xs px-2 py-1 rounded">Active</span></td>
                <td>
                <button class="text-sm border px-2 py-1 rounded mr-1">View</button>
                <button class="text-sm border px-2 py-1 rounded">Renew</button>
                </td>
                </tr>
                `;
        list.appendChild(card);
      });
    });
}
    });


