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

function abrcPmHome() {
	if (this === window) {
		return new abrcPmHome();
	} else {
		return this;
	}
}

abrcPmHome.prototype = {
	
	btnRequestInvite: "#btn-request-invite",
	
	requestInvite: "#request-invite",
	
	btnSendInviteRequest: "#btn-send-request",
	
	btnCreateNewUser: "#signup",
	
	init: function() {
		var that = this;
		
		// Fix input element click problem
		$('.dropdown input, .dropdown label').click(function(e) {
			e.stopPropagation();
		});
		
		// create a click event that shows a form so that a user
		// can request an invitation to use the system.
		$(that.btnRequestInvite).click(function() {
			$(that.requestInvite).show();
		});
		
		// create a click event that will run code to send the 
		// user's request for membership.
		$(that.btnSendInviteRequest).click(function() {
			var firstNameRequest = $("#firstNameRequest").val();
			var lastNameRequest = $("#lastNameRequest").val();
			var emailRequest = $("#emailRequest").val();
			
			if (emailRequest != "" && lastNameRequest != "" && firstNameRequest != "" && that.validateEmail(emailRequest)) {
				abrcPm.users.requestInvitation(emailRequest, firstNameRequest, lastNameRequest)
					.done(function() {
						$(that.requestInvite).hide();
						$("#successRequest").show();
						$(that.btnRequestInvite).off('click');
					})
					.fail(function() {
						$(that.requestInvite).hide();
						$("#failureRequest").show();
					});
				// reset the form
				$("#firstNameRequest").val("");
				$("#lastNameRequest").val("");
				$("#emailRequest").val("");
			}
		});
		
		// create a click event that will run code to create
		// a new user.
		$(that.btnCreateNewUser).click(function() {
			var firstnameSignup = $("#firstnameSignup").val();
			var lastnameSignup = $("#lastnameSignup").val();
			var emailSignup = $("#emailSignup").val();
			var usernameSignup = $("#usernameSignup").val();
			var passwordSignup = $("#passwordSignup").val();
			var passwordconfirmSignup = $("#passwordconfirmSignup").val();
			
			var okay = false;
			var success = false;
			
			if (passwordSignup === passwordconfirmSignup && that.validateEmail(emailSignup)) {
				okay = true;
			}
			
			if (okay) {
				abrcPm.users.add(firstnameSignup, lastnameSignup, usernameSignup, emailSignup, passwordSignup)
					.done(function() {
						success = true;
					})
					.always(function(data, textStatus) {
						if (success) {
							$("#firstnameSignup").val("");
							$("#lastnameSignup").val("");
							$("#emailSignup").val("");
							$("#usernameSignup").val("");
							$("#passwordSignup").val("");
							$("#passwordconfirmSignup").val("");
							$("#user-success").show();
							$("#user-info").show();
							$("#init-success").hide();
							$("#init-warning").hide();
						} else {
							$("#usernameSignup").val("");
							$("#passwordSignup").val("");
							$("#passwordconfirmSignup").val("");
							$("#user-error-message").html(data.responseText);
							$("#user-failure").show();
						}
					});
			}
		});
		
		// Django handles logging in.
		
		return that;
	},
	
	validateEmail: function(email) {
		var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	    if (re.test(email)) {
	    	// TODO: run AJAX to get invited email address (returns boolean)
	    	// for now, just return true.
	    	return true;
	    }
	    return false;
	},
	
};

var home = abrcPmHome().init();
