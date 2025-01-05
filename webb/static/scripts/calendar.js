document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar-container');

    // Initialize FullCalendar
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        editable: {{ 'true' if can_edit_shared else 'false' }},
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek,dayGridDay'
        },
        timezone: 'Asia/Bangkok',  // Adjust timezone if needed
        events: function(info, successCallback, failureCallback) {
            fetch('/dashboard/scheduling/get-events')
                .then(response => response.json())
                .then(events => {
                    successCallback(events);
                })
                .catch(error => failureCallback(error));
        },
        eventClick: function(info) {
          // Show the modal with event details
          $('#eventModal').modal('show');
          
          // Extract event start and end times (in local time)
          const eventStart = new Date(info.event.start);
          const eventEnd = new Date(info.event.end);
          
          // Helper function to format time as HH:MM
          function formatTime(date) {
              let hours = date.getHours().toString().padStart(2, '0');
              let minutes = date.getMinutes().toString().padStart(2, '0');
              return `${hours}:${minutes}`;
          }
      
          // Format the start and end times to `YYYY-MM-DD` and `HH:MM`
          const localStartDate = eventStart.toLocaleDateString('en-CA'); // Format as YYYY-MM-DD
          const localStartTime = formatTime(eventStart); // Format as HH:MM
          
          const localEndDate = eventEnd.toLocaleDateString('en-CA'); // Format as YYYY-MM-DD
          const localEndTime = formatTime(eventEnd); // Format as HH:MM
      
          // Populate the modal fields with event details
          document.getElementById('event-title').value = info.event.title;
          document.getElementById('event-start-date').value = localStartDate;
          document.getElementById('event-start-time').value = localStartTime;
          document.getElementById('event-end-date').value = localEndDate;
          document.getElementById('event-end-time').value = localEndTime;
      
          // Set the event ID for editing
          document.getElementById('event-id').value = info.event.id;
      
          // Add the delete event button functionality
          document.getElementById('delete-event').onclick = function() {
              deleteEvent(info.event.id);
          };
      }
           
    });

    calendar.render();

    // Event handler for adding new events
    document.getElementById('add-event').addEventListener('click', function() {
        $('#eventModal').modal('show');
        document.getElementById('event-form').reset();  // Clear form for new events
        document.getElementById('event-id').value = ''; // Clear the ID for new events
    });

    // Event handler for saving the event (either add or update)
    document.getElementById('save-event').addEventListener('click', function() {
        var title = document.getElementById('event-title').value;
        var startDate = document.getElementById('event-start-date').value;
        var startTime = document.getElementById('event-start-time').value;
        var endDate = document.getElementById('event-end-date').value;
        var endTime = document.getElementById('event-end-time').value;
        var eventId = document.getElementById('event-id').value;

        if (title && startDate && startTime && endDate && endTime) {
            var startDateTime = new Date(startDate + 'T' + startTime + ':00');
            var endDateTime = new Date(endDate + 'T' + endTime + ':00');

            var eventData = {
                title: title,
                start: startDateTime.toISOString(),
                end: endDateTime.toISOString()
            };

            if (eventId) {
                // If event ID exists, update the event
                eventData.id = eventId;
                fetch('/dashboard/scheduling/update-event', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(eventData),
                })
                .then(response => response.json())
                .then(data => {
                    // Update event in calendar
                    var event = calendar.getEventById(data.id);
                    event.setProp('title', data.title);
                    event.setStart(data.start);
                    event.setEnd(data.end);
                })
                .catch(error => {
                    console.error('Error updating event:', error);
                    alert('There was an error updating the event.');
                });
            } else {
                // If no event ID, create a new event
                fetch('/dashboard/scheduling/add-event', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(eventData),
                })
                .then(response => response.json())
                .then(data => {
                    // Add event to calendar
                    calendar.addEvent({
                        id: data.id,
                        title: data.title,
                        start: data.start,
                        end: data.end,
                        allDay: false
                    });
                })
                .catch(error => {
                    console.error('Error adding event:', error);
                    alert('There was an error adding the event.');
                });
            }

            // Close modal after saving
            $('#eventModal').modal('hide');
        } else {
            alert('Please fill in all fields.');
        }
    });
});

function deleteEvent(eventId) {
    // Send a POST request to the backend to delete the event
    fetch('/dashboard/scheduling/delete-event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: eventId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Event deleted successfully');
            window.location.reload();
        } else {
            alert('Failed to delete event');
        }
    })
    .catch(error => {
        console.error('Error deleting event:', error);
    });
}
