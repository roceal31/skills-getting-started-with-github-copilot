document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsList = details.participants
          .map(email => `<li data-email="${email}" data-activity="${name}"><button class="delete-btn" aria-label="Remove ${email} from activity">✕</button> ${email}</li>`)
          .join("");

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Registered Participants:</strong>
            <ul class="participants-list">
              ${participantsList}
            </ul>
          </div>
        `;

        // Attach delete handlers
        activityCard.querySelectorAll(".delete-btn").forEach(btn => {
          btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const li = btn.closest("li");
            const email = li.getAttribute("data-email");
            const activity = li.getAttribute("data-activity");
            
            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activity)}/withdraw?email=${encodeURIComponent(email)}`,
                { method: "DELETE" }
              );
              
              if (response.ok) {
                messageDiv.textContent = `Successfully withdrew ${email} from ${activity}`;
                messageDiv.className = "success";
                messageDiv.classList.remove("hidden");
                
                // Refresh activities
                setTimeout(() => {
                  messageDiv.classList.add("hidden");
                  fetchActivities();
                }, 2000);
              } else {
                const result = await response.json();
                messageDiv.textContent = result.detail || "Failed to withdraw";
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
              }
            } catch (error) {
              messageDiv.textContent = "Failed to withdraw. Please try again.";
              messageDiv.className = "error";
              messageDiv.classList.remove("hidden");
              console.error("Error withdrawing:", error);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
