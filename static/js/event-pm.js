/**
 * ABRC PM Javascript Webapp
 * 
 * Create an easy-to-use interface to the entire ABRC API.
 * 
 * Recommended Uses:
 * 
 * 1. Keep track of divs that are of importance such as adding new table entries
 * 2. Show / Hide certain information at certain times.
 * 3. Break the javascript functionality into 2 different camps (logged in users / non-logged in users)
 * 		-- adminPm.user.delete ... etc...
 * 		-- abrcPm.users.create ... etc...
 * 4. Make sure that along with client side we keep the integrity on the server as well.
 * 
 * REQUIRES: pm-api-client.js, jQuery, json2
 * 
 * @author: Chris Bartos <bartos.25@osu.edu>
 */
function abrcPmEvent() {
	if (this === window) {
		return new abrcPmEvent();
	} else {
		return this;
	}
}


abrcPmEvent.prototype = {
	init: function() {
		var that = this;
		return that;
	},
	
	addAttendee: function(event_id, attendee_id) {
		abrcPm.events.get(event_id)
			.done(function(data) {
				// get the attendee array append new attendee
				var attendees = [];
				for (var i in data["attendees"]) {
					attendees.push(data["attendees"][i]["resource_uri"]);
				}
				attendees.push(ajaxApi.getBaseDir()+"user/"+attendee_id+"/");
				abrcPm.events.addAttendee(event_id, attendees)
					.done(function(data) {
						location.reload();
					});
			});
	},
	
	removeAttendee: function(event_id, attendee_id) {
		abrcPm.events.get(event_id)
			.done(function(data) {
				// get the attendee array append new attendee
				var attendees = [];
				for (var i in data["attendees"]) {
					if (attendee_id == data["attendees"][i]["id"]) {
						continue;
					}
					attendees.push(data["attendees"][i]["resource_uri"]);
				}
				abrcPm.events.addAttendee(event_id, attendees)
					.done(function(data) {
						location.reload();
					});
			});
	},
}

var events = abrcPmEvent().init();