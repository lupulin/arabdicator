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

function abrcPmSystem() {
	if (this === window) {
		return new abrcPmSystem();
	} else {
		return this;
	}
}


abrcPmSystem.prototype = {
	
	projectTable: "#project-table",
	
	myIssueTable: "#my-issue-table",
	
	allIssueTable: "#all-issue-table",
	
	projectData: null,
	
	me: null,
	
	globType: "all",
	
	globWhich: null,
	
	init: function() {
		var that = this;
		
		var oneMinute = 1000*60;
		
		abrcPm.issues.generatePriorityDropdown(".priority");
		abrcPm.issues.generateResolutionDropdown(".resolution");
		abrcPm.issues.generateStatusDropdown(".status");
		abrcPm.projects.generateProjectDropdown(".project");
		abrcPm.issues.generateIssueTypeDropdown(".issuetype");
		if (window.issue) { abrcPm.templates.generateTemplateDropdown("#template-dropdown"); }
		
		that.populateTables();
		
		// setInterval(that.updateTables, oneMinute);
		
		// Date stuff
		var startDateTextBox = $('#start-event-date');
		var endDateTextBox = $('#end-event-date');
		var editStartDateTextBox = $('#edit-start-event-date');
		var editEndDateTextBox = $('#edit-end-event-date');
		
		startDateTextBox.datetimepicker({ 
			onClose: function(dateText, inst) {
				if (endDateTextBox.val() != '') {
					var testStartDate = startDateTextBox.datetimepicker('getDate');
					var testEndDate = endDateTextBox.datetimepicker('getDate');
					if (testStartDate > testEndDate)
						endDateTextBox.datetimepicker('setDate', testStartDate);
				}
				else {
					endDateTextBox.val(dateText);
				}
			},
			onSelect: function (selectedDateTime){
				endDateTextBox.datetimepicker('option', 'minDate', startDateTextBox.datetimepicker('getDate') );
			}
		});
		endDateTextBox.datetimepicker({ 
			onClose: function(dateText, inst) {
				if (startDateTextBox.val() != '') {
					var testStartDate = startDateTextBox.datetimepicker('getDate');
					var testEndDate = endDateTextBox.datetimepicker('getDate');
					if (testStartDate > testEndDate)
						startDateTextBox.datetimepicker('setDate', testEndDate);
				}
				else {
					startDateTextBox.val(dateText);
				}
			},
			onSelect: function (selectedDateTime){
				startDateTextBox.datetimepicker('option', 'maxDate', endDateTextBox.datetimepicker('getDate') );
			}
		});
		
		editStartDateTextBox.datetimepicker({ 
			onClose: function(dateText, inst) {
				if (editEndDateTextBox.val() != '') {
					var testStartDate = editStartDateTextBox.datetimepicker('getDate');
					var testEndDate = editEndDateTextBox.datetimepicker('getDate');
					if (testStartDate > testEndDate)
						editEndDateTextBox.datetimepicker('setDate', testStartDate);
				}
				else {
					editEndDateTextBox.val(dateText);
				}
			},
			onSelect: function (selectedDateTime){
				editEndDateTextBox.datetimepicker('option', 'minDate', editStartDateTextBox.datetimepicker('getDate') );
			}
		});
		editEndDateTextBox.datetimepicker({ 
			onClose: function(dateText, inst) {
				if (editStartDateTextBox.val() != '') {
					var testStartDate = editStartDateTextBox.datetimepicker('getDate');
					var testEndDate = editEndDateTextBox.datetimepicker('getDate');
					if (testStartDate > testEndDate)
						editStartDateTextBox.datetimepicker('setDate', testEndDate);
				}
				else {
					editStartDateTextBox.val(dateText);
				}
			},
			onSelect: function (selectedDateTime){
				editStartDateTextBox.datetimepicker('option', 'maxDate', editEndDateTextBox.datetimepicker('getDate') );
			}
		});
		
		abrcPm.users.generateUserDropdown(".staff");
		
		that.saveMe();
		
		$(".edit").hide();
		$(".issue-station").hover(function() {
			$(".edit").show();
		}, function() {
			$(".edit").hide();
		});
		
		$("#issue-filter").on('keypress', function(e) {
			if (e.which == 13) {
				$("li").removeClass("active");
				system.populateIssuesTable("search", $("#issue-filter").val(), "my-issue-table", true);
				system.populateProjectIssuesTable("search", $("#issue-filter").val(), "all-project-issue-table");
			}
		});
		
		$('a[data-toggle="tab"]').on('shown', function (e) {
			
			var that = this;
			
			e.preventDefault();
			
		  	var data = e.target.toString().match(/#(.+)/i)[1];
		  
		  	$("#issue-filter").val("");
		  
		  	// figure out the type of thing we are filtering by
		  	var typeData = data.split('-');
		 	type = typeData[0];
		  	which = typeData[1];
		  
		  	$("#my-issue-table").html("<img src='/static/img/ajax-spinner.gif' />");
		  
		  	if (that.globType == "all") {
		  		if (window.user_id) {
		  			system.populateIssuesTable("user", window.user_id, "my-issue-table", false);
		  		} else {
		  			system.populateIssuesTable("all", null, "my-issue-table", true);
		  		}
		  	}
		  
		  	// if type is assigned or reporter, do something else
		  	if (type == "assigned" || type == "reported") {
		  		which = system.me.id;
		  	}
		  	if (window.user_id) {
		  		if (type == "all") {
					system.populateIssuesTable("user", window.user_id, "my-issue-table", false);
				} else {
					system.populateIssuesTable(type, which+"&user="+window.user_id, "my-issue-table", false);
				}
			} else {
				system.populateIssuesTable(type, which, "my-issue-table", true);
				system.populateProjectIssuesTable(type, which, "all-project-issue-table");
			}
		});
		
		$("#change_html").off('change').change(function(e) {
			e.preventDefault();
			
			$("#no_html").toggle('fast');
			$("#use_html").toggle('fast');
		});
		
		$("#create-project").off('click').click(function(e) {
			
			var projectKey = $("#project-key").val();
			var projectLead = $("#user-dropdown").val();
			var projectName = $("#project-name").val();
			var projectDesc = $("#project-description").val();
			
			e.preventDefault();
			
			if (projectKey != "" && projectLead != "" && projectName != "") {
			
				abrcPm.projects.add(projectName, projectDesc, projectKey, projectLead)
					.complete(function(data) {
						
						$("#project-key").val("");
						$("#user-dropdown").val("");
						$("#project-name").val("");
						$("#project-description").val("");
						system.populateTables();
						$(".modal").modal("hide");
					});
			}
			
		});
		
		$("#create-issue").off('click').click(function(e) {
			
			var reporter = system.me["id"];
			var projectName = $("#create-issue-project select").val();
			var issueName = $("#create-issue-name").val();
			var description = $("#create-issue-description").val();
			var priority = $("#create-issue-priority select").val();
			var issueType = $("#create-issue-issuetype select").val();
			var resolution = 6;
			var status = 1;
			
			e.preventDefault();
			
			if (reporter != "" && projectName != "" && issueName != "" &&  priority != "" && issueType != "") {
				
				abrcPm.issues.add(issueName, projectName, description, resolution, priority, issueType, status, reporter)
					.done(function(data) {
						system.populateTables();
						$("#create-issue-name").val("");
						$("#create-issue-description").val("");
						$(".modal").modal("hide");
						
						abrcPm.issues.get(null, issueName)
							.done(function(data) {
								location.href="/pm/issue_details/"+data["objects"][0]["id"]+"/";
							});
					});
			}
		});
		
		$("#add-users").off('click').click(function(e) {
			e.preventDefault();
			that.createInvitationTable()
		});
		
		$("#create-event").off('click').click(function(e) {
			
			var eventName = $("#create-event-name").val();
			var eventDesc = $("#create-event-description").val();
			var eventLoca = $("#create-event-location").val();
			var startEventDate = $("#start-event-date").val();
			var endEventDate = $("#end-event-date").val();
			
			startEventDate = abrcPm.events.formatDate(startEventDate);
			endEventDate = abrcPm.events.formatDate(endEventDate);
			
			e.preventDefault();
			
			if (eventName != "") {
				abrcPm.events.add(eventName, eventDesc, eventLoca, startEventDate, endEventDate)
					.done(function(data) {
						system.populateTables();
						$("#create-event-name").val("");
						$("#create-event-description").val("");
						$("#create-event-location").val("");
						$("#start-event-date").val("");
						$("#end-event-date").val("");
						$(".modal").modal("hide");
					});
			}
			
		});
		
		$(function() {
		    $('.timepicker').datetimepicker({
		      language: 'en',
		      pick12HourFormat: true,
		      pickDate: false
		    });
		    
		    $('.datepicker').datetimepicker({
		      language: 'en',
		      pickTime: false
		    });
		  });
		
		return that;
	},
	
	populateTemplateTable: function() {
		
		$("#create-template").hide('fast');
		$("#edit-template").hide('fast');
		$("#template-table").show('fast');
		
		abrcPm.templates.all()
			.done(function(data) {
				
				var tempTable = $("#template-table");
				
				if (data["objects"].length == 0) {
					tempTable.html("There are no templates");
				}
	
				var templateTable = $("<table />", {"class": "table table-striped table-bordered table-hover",
										   		    "style": "width: 100%"});
				
				var templateHeader = $("<tr />").appendTo($("<thead />").appendTo(templateTable));
				$("<th />", {"text": "Name"}).appendTo(templateHeader);
				$("<th />", {"text": ""}).appendTo(templateHeader);
				
				var tableBody = $("<tbody />").appendTo(templateTable);
				
				for (var i in data["objects"]) {
					var templateBody = $("<tr />").appendTo(tableBody);
					$("<td />", {"text": data["objects"][i]["name"]}).appendTo(templateBody);
					$("<a />", {"text": "Edit", 
								"href": "#", 
								"onclick": "system.editTemplate("+ data["objects"][i]["id"] +")"
							   }).appendTo($("<td />").appendTo(templateBody));
					$("<a />", {"text": "Delete", 
								"href": "#", 
								"onclick": "system.deleteTemplate("+ data["objects"][i]["id"] +")"
							   }).appendTo($("<td />").appendTo(templateBody));
				}
					
				tempTable.html(templateTable);
				
				$("#add-template").modal('show');
			    
			    $("<button />", {"text": "Add Template",
			    				 "class": "btn btn-primary",
			    				 "id": "create-new-template-btn"}).appendTo(tempTable);
			    $("#create-new-template-btn").off('click').on('click', function(e) {
			    	e.preventDefault();
			    	system.addNewTemplate();
			    });
		});
	},
	
	deleteTemplate: function(template_id) {
		abrcPm.templates.deleteTemplate(template_id)
			.done(function(data) {
				system.populateTemplateTable();
				abrcPm.templates.generateTemplateDropdown('#template-dropdown');
			});
	},
	
	editTemplate: function(template_id) {
		$("#template-table").hide('fast');
		$("#edit-template").show('fast');
		
		abrcPm.templates.get(template_id)
			.done(function(data) {
				$("#edit-template-name").val(data["name"]);
				$("#edit-template-text").val(data["template"]);
				
				$("#edit-template-btn").off('click').on('click', function(e) {
					e.preventDefault();
					
					var template = $("#edit-template-text").val();
					var name = $("#edit-template-name").val();
					
					if (template != "" && name != "") {
						abrcPm.templates.edit(template_id, name, template)
							.done(function(data) {
								system.populateTemplateTable();
								$("#template-table").show('fast');
								$("#edit-template").hide('fast');
								abrcPm.templates.generateTemplateDropdown('#template-dropdown');
							});
						$("#edit-template-name").val("");
						$("#edit-template-text").val("");
					}
				});
			});
	},
	
	addNewTemplate: function() {
		
		$("#template-table").hide('fast');
		$("#create-template").show('fast');
		
		$("#create-template-btn").off('click').on('click', function(e) {
			e.preventDefault();
			
			var template = $("#new-template").val();
			var name = $("#template-name").val();
			
			if (template != "" && name != "") {
				abrcPm.templates.add(name, template)
					.done(function(data) {
						system.populateTemplateTable();
						$("#template-table").show('fast');
						$("#create-template").hide('fast');
						abrcPm.templates.generateTemplateDropdown("#template-dropdown");
					});
					
				$("#new-template").val("");
				$("#template-name").val("");
			}
			
		});
	},
	
	updateTables: function() {
		abrcPm.projects.all()
			.done(function(data) {
				system.populateProjectTable(data);
			});
		system.populateIssuesTable(system.globType, system.globWhich, "my-issue-table", true);
		// system.populateIssuesTable("all", null, "all-issue-table", false);
		system.populateEventsTable("upcoming-events");
				
		abrcPm.activity.all()
			.done(function(data) {
				system.populateActivityTable(data, "recent-activity");
				
			});
	},
	
	editProfile: function() {
		
		$("#editProfile").modal('show');
		
		$("#edit-firstname").val(that.me.first_name);
		$("#edit-lastname").val(that.me.last_name);
		$("#edit-username").val(that.me.username);
		$("#edit-email").val(that.me.email);
		
		$("#edit-profile-btn").off('click').click(function(e) {
			
			e.preventDefault();
			
			// that and this are no longer in scope.
			var userId = system.me.id;
			var firstName = $("#edit-firstname").val();
			var lastName = $("#edit-lastname").val();
			var username = $("#edit-username").val();
			var email = $("#edit-email").val();
			
			abrcPm.users.profileEdit(userId, firstName, lastName, username, email)
 				.done(function(data) {
 					system.saveMe();
 				});
 			
			$("#editProfile").modal('hide');
		});
	},
	
	editEmailServer: function() {
		
		$("#editEmailServer").modal('show');
		
		abrcPm.emailserver.all()
			.done(function(data) {
				
				$("#edit-emailserver-name").val(data["objects"][0]["name"]);
				$("#edit-emailserver-host").val(data["objects"][0]["hostname"]);
				$("#edit-emailserver-email").val(data["objects"][0]["email"]);
				$("#edit-emailserver-port").val(data["objects"][0]["port"]);
				$("#edit-emailserver-username").val(data["objects"][0]["username"]);
				$("#edit-emailserver-password").val(data["objects"][0]["password"]);
				
				window.emailserverId = data["objects"][0]["id"];
			});
			
		$("#edit-emailserver-btn").off('click').click(function(e) {
			
			e.preventDefault();
			
			var id = emailserverId;
			var name = $("#edit-emailserver-name").val();
			var host  = $("#edit-emailserver-host").val();
			var email = $("#edit-emailserver-email").val();
			var port = $("#edit-emailserver-port").val();
			var username = $("#edit-emailserver-username").val();
			var password = $("#edit-emailserver-password").val();
			
			abrcPm.emailserver.edit(id, name, host, email, port, username, password)
				.done(function(data) {					
					$("#editEmailServer").modal('hide');					
				});
		});
	},
	
	createInvitationTable: function() {
		
		abrcPm.users.getInvitations()
				.done(function(data) {
					
					if (data["objects"].length == 0) {
						$("#invitations").html("There are no invitations");
						$("#invitationsModal").modal('show');
						return;
					}
					
					var inviteTable = $("<table />", {"class": "table table-striped table-bordered table-hover",
								   		  			  "style": "width: 100%"});
								   		  
					var inviteHeader = $("<tr />").appendTo($("<thead />").appendTo(inviteTable));
					$("<th />", {"text": "Last Name"}).appendTo(inviteHeader);
					$("<th />", {"text": "First Name"}).appendTo(inviteHeader);
					$("<th />", {"text": "Email"}).appendTo(inviteHeader);
					$("<th />", {"text": ""}).appendTo(inviteHeader);
					$("<th />", {"text": ""}).appendTo(inviteHeader);
					
					var tableBody = $("<tbody />").appendTo(inviteTable);
					
					for (var i in data["objects"]) {
						var inviteBody = $("<tr />").appendTo(tableBody);
						$("<td />", {"text": data["objects"][i]["lastname"]}).appendTo(inviteBody);
						$("<td />", {"text": data["objects"][i]["firstname"]}).appendTo(inviteBody);
						$("<td />", {"text": data["objects"][i]["email"]}).appendTo(inviteBody);
						$("<a />", {"text": "Accept", 
									"href": "#", 
									"onclick": "system.acceptInvitationRequest("+ data["objects"][i]["id"] +")"
								   }).appendTo($("<td />").appendTo(inviteBody));
						$("<a />", {"text": "Reject", 
									"href": "#", 
									"onclick": "system.rejectInvitationRequest("+ data["objects"][i]["id"] +")"
								   }).appendTo($("<td />").appendTo(inviteBody));
					}
					
					$("#invitations").html(inviteTable);
					
					$("#invitationsModal").modal('show');
				});
	},
	
	editIssue: function(issue_id) {
		
		abrcPm.issues.get(issue_id).done(function(data) {
			$("#edit-issue-name").val(data["name"]);
			$("#edit-issue-description").val(data["description"]);
			$("#edit-issue-reporter").val(data["reporter"]["formatted_user"]);
			window.reporterId = data["reporter"]["id"];
			abrcPm.issues.generatePriorityDropdown(".priority", data["priority"]["id"]);
			abrcPm.issues.generateResolutionDropdown(".resolution", data["resolution"]["id"]);
			abrcPm.issues.generateStatusDropdown(".status", data["status"]["id"]);
			abrcPm.projects.generateProjectDropdown(".project", data["project"]["id"]);
			abrcPm.issues.generateIssueTypeDropdown(".issuetype", data["type"]["id"]);
			
			$("#edit-issue").off('click').click(function(e) {
				var reporter = window.reporterId;
				var projectName = $("#edit-issue-project select").val();
				var issueName = $("#edit-issue-name").val();
				var description = $("#edit-issue-description").val();
				var priority = $("#edit-issue-priority select").val();
				var issueType = $("#edit-issue-type select").val();
				var resolution = $("#edit-issue-resolution select").val();
				var status = $("#edit-issue-status select").val();
				
				e.preventDefault();
				
				if (reporter != "" && projectName != "" && issueName != "" &&  priority != "" && issueType != "") {
					
					abrcPm.issues.edit(issue_id, projectName, issueName, description, resolution, priority, issueType, status, reporter)
						.done(function(data) {
							system.populateTables();
							$(".modal").modal("hide");
						});
				}
			});
		});
	},
	
	acceptInvitationRequest: function(invite_id) {
		
		abrcPm.users.acceptInvitationRequest(invite_id)
			.done(function(data) { 
				system.createInvitationTable();
			});
		
	},
	
	rejectInvitationRequest: function(invite_id) {
		
		abrcPm.users.rejectInvitationRequest(invite_id)
			.done(function(data) {
				system.createInvitationTable();
			});
		
	},
	
	createComment: function(issue_id) {
		user_id = system.me.id;
		staffOnlyComment = system._emailStaffOnly();
		var comment = $.trim($("#create-comment-text").val());
		if (comment == "") { return; }
		abrcPm.comments.add(issue_id, comment, user_id, staffOnlyComment)
			.done(function() {
				location.reload();
				$("#create-comment-text").val("");
			});
	},
	
	editProject: function(project_id) {
		
		abrcPm.projects.get(project_id).done(function(data) {
			$("#edit-project-key").val(data["key"]);
			$("#edit-project-name").val(data["name"]);
			$("#edit-project-description").val(data["description"]);
			abrcPm.users.generateUserDropdown('.lead', data["lead"]["id"]);
		});
		
		$("#edit-project").off('click').click(function(e) {
			
			e.preventDefault();
			
			var projectKey  = $("#edit-project-key").val();
			var projectLead = $(".lead #user-dropdown").val();
			var projectName = $("#edit-project-name").val();
			var projectDesc = $("#edit-project-description").val();
			
			if (projectKey != "" && projectLead != "" && projectName != "") {
			
				abrcPm.projects.edit(project_id, projectName, projectDesc, projectKey, projectLead)
					.complete(function(data) {
						
						$("#project-key").val("");
						$(".lead #user-dropdown").val("");
						$("#project-name").val("");
						$("#project-description").val("");
						system.populateTables();
						$(".modal").modal("hide");
					});
			}
			
		});
		
	},
	
	editEvent: function(event_id) {
		
		abrcPm.events.get(event_id).done(function(data) {
			$("#edit-event-name").val(data["name"]);
			$("#edit-event-description").val(data["description"]);
			$("#edit-event-location").val(data["location"]);
			$("#edit-start-event-date").val(abrcPm.events.unformatDate(data["date"]));
			$("#edit-end-event-date").val(abrcPm.events.unformatDate(data["end_date"]));
			
			$("#edit-event").off('click').click(function(e) {
				e.preventDefault();
				
				var eventName = $("#edit-event-name").val();
				var eventDesc = $("#edit-event-description").val();
				var eventLoca = $("#edit-event-location").val();
				var startEventDate = $("#edit-start-event-date").val();
				var endEventDate = $("#edit-end-event-date").val();
				
				// format date and time to acceptable values
				startEventDate = abrcPm.events.formatDate(startEventDate);
				endEventDate = abrcPm.events.formatDate(endEventDate);
				
				if (eventName != "") {
					abrcPm.events.edit(event_id, eventName, eventDesc, eventLoca, startEventDate, endEventDate)
						.done(function(data) {
							system.populateTables();
							$(".modal").modal("hide");	
							$("#edit-event").off('click');	
						});
				}
			});
		});
	},
	
	populateProjectTable: function(data) {
		// create a table and append it to #project-table
		var projectTableHtml = $("<table />", {"class": "table table-striped table-bordered table-hover",
											   "style": "width: 100%"});
		var tableHeaders = $("<thead />").appendTo(projectTableHtml);
		$("<th />", {"text": "Name"}).appendTo(tableHeaders);
		$("<th />", {"text": "Lead"}).appendTo(tableHeaders);
		$("<th />", {"text": "Issues"}).appendTo(tableHeaders);
		$("<th />", {"text": ""}).appendTo(tableHeaders);
		var tableBody = $("<tbody />").appendTo(projectTableHtml);
		if (data["objects"].length == 0) {
			$("#project-table").html("There are no projects available");
			return;
		}
		for (var u in data["objects"]) {
			var tableRow = $("<tr />", {"class": "project"+data["objects"][u]["id"]}).appendTo(tableBody);
			$("<a />", {"text": data["objects"][u]["name"], href: "/pm/project_details/"+data["objects"][u]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
			$("<a />", {"text": data["objects"][u]["lead"]["formatted_user"], href: "/pm/user_details/"+data["objects"][u]["lead"]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
			$("<td />", {"text": data["objects"][u]["issueCount"]}).appendTo(tableRow);
			var iconsElement = $("<span />", {"class": "dropdown"}).appendTo($("<td />", {"width": "35px"}).appendTo(tableRow));
			$("<i />", {"class": "icon-wrench"})
				.appendTo($("<a />", {"href": "#", "class": "dropdown-toggle", "data-toggle": "dropdown"})
				.appendTo(iconsElement));
				
			var dropdownElement = $("<ul />", {"class": "dropdown-menu"}).appendTo(iconsElement);
			$("<a />", 
				{"href": "#", 
				 "onclick": "javascript:system.changeSelectedProject("+ data["objects"][u]["id"] +")", 
				 "data-toggle": "modal", 
				 "data-target": "#newissue", 
				 "text": "Add Issue"})
				 .appendTo($("<li />")
				 .appendTo(dropdownElement));
			$("<a />", 
				{"href": "#", 
				 "onclick": "javascript:system.createSearchWordTable("+data["objects"][u]["id"]+")", 
				 "data-toggle": "modal", 
				 "data-target": "#searchwords", 
				 "text": "Change search words"})
				 .appendTo($("<li />")
				 .appendTo(dropdownElement));
			$("<a />", 
				{"href": "#",
				 "onclick": "javascript:system.editProject("+ data["objects"][u]["id"] +")", 
				 "data-toggle": "modal", 
				 "data-target": "#editproject", 
				 "text": "Edit Project"})
				 .appendTo($("<li />")
				 .appendTo(dropdownElement));
			$("<a />", 
				{"href": "/pm/project_details/"+data["objects"][u]["id"]+"/",
				 "text": "Project Details"})
				 .appendTo($("<li />")
				 .appendTo(dropdownElement));	 
			$("<i />", {"class": "icon-remove"})
				.appendTo($("<a />", 
				{"href": "javascript:void(0);", 
				 "onclick": "javascript:system.deleteProjectUpdateTable("+ data["objects"][u]["id"] +")"})
				.appendTo(iconsElement));
		}
		$("#project-table").html(projectTableHtml);
	},
	
	populateTables: function(data) {			
		abrcPm.projects.all()
			.done(function(data) {
				system.populateProjectTable(data);
				if (window.user_id) {
					system.populateIssuesTable("user", window.user_id, "my-issue-table", false);	
				} else {
					system.populateIssuesTable("all", null, "my-issue-table", true);
				}
				system.populateProjectIssuesTable("all", null, "all-project-issue-table");
				system.populateEventsTable("upcoming-events");
						
						abrcPm.activity.all()
							.done(function(data) {
								system.populateActivityTable(data, "recent-activity");
								
							});
			});
	},
	
	appendToIssueTables: function(div, offset) {
		ajaxApi.executeAjax(offset, "GET", null)
			.done(function(data) { 
				
				var moreThan20 = false;
					if (data["meta"]["next"] != null) {
						moreThan20 = true;
					}
				var tableBody = $("#"+div+" table tbody");
				
				for (var u in data["objects"]) {
					
					var args = {};
					if (data["objects"][u]["status"]["name"] == "Closed") {
						args["class"] = "info";
					} else if (data["objects"][u]["status"]["name"] == "In Progress") {
						args["class"] = "warning";
					} else if (data["objects"][u]["status"]["name"] == "Resolved") {
						args["class"] = "success";
					} else {
						args["class"] = "error";
					}
					args["class"] = args["class"]+" event"+data["objects"][u]["id"];
					args["id"] = data["objects"][u]["id"];
					var tableRow = $("<tr />", args).appendTo(tableBody);
					$("<td />", {text: data["objects"][u]["issue_key"]}).appendTo(tableRow);
					var reporter = "";
					if (data["objects"][u]["reporter"]["first_name"] == "Anonymous") {
						reporter = data["objects"][u]["reporter"]["email"];
					} else {
						reporter = data["objects"][u]["reporter"]["first_name"] + " " + data["objects"][u]["reporter"]["last_name"];
					}
					$("<td />", {"text": reporter}).appendTo(tableRow);
					if (system.me.id == data["objects"][u]["reporter"]["id"]) {
						$("<td />", {text: "Reporter"}).appendTo(tableRow);
					} else {
						$("<td />", {text: "Assignee"}).appendTo(tableRow);
					}
					$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["pub_date"]) + " " + abrcPm.events.getTime(data["objects"][u]["pub_date"])}).appendTo(tableRow);
					$("<a />", {"text": data["objects"][u]["project"]["name"], href: "/pm/project_details/"+data["objects"][u]["project"]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<a />", {"text": data["objects"][u]["name"], href: "/pm/issue_details/"+data["objects"][u]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<td />", {"text": data["objects"][u]["type"]["name"]}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["status"]["name"]}).appendTo(tableRow);
					var resolution = data["objects"][u]["resolution"]["name"];
					if (resolution == "Fixed") {
						resolution += " ("+ abrcPm.events.getDate(data["objects"][u]["fixed"]) +")";
					}
					$("<td />", {"text": resolution}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["priority"]["name"]}).appendTo(tableRow);
					var iconsElement = $("<td />", {width: "35px"}).appendTo(tableRow);
					if (system._issueAssignedToMe(data["objects"][u])) {
						$("<i />", {"class": "icon-wrench"}).appendTo($("<a />", {"href": "#",
					 															"onclick": "javascript:system.editIssue("+ data["objects"][u]["id"] +")", 
					 															"data-toggle": "modal", 
					 															"data-target": "#editissue"}).appendTo(iconsElement));
						$("<i />", {"class": "icon-remove"}).appendTo($("<a />", {href: "javascript:void(0);", onclick: "javascript:system.deleteIssueUpdateTable("+ data["objects"][u]["id"] +")"}).appendTo(iconsElement));
					} else {
						$("<i />", {"class": "icon-question-sign"}).appendTo($("<a />", {"href": "#", "rel": "tooltip", "class": 'tip', "title": "You cannot edit this issue because it is not assigned to you."}).appendTo(iconsElement));
						
					}
				}
				
				if (moreThan20) {
					$("#more-issues").show('fast');
					$("#more-issues").off('click').on('click', function(e) {
						e.preventDefault();
						system.appendToIssueTables(div, data["meta"]["next"]);
					});
				} else {
					$("#more-issues").hide('fast');
				}
			});
	},
	
	appendToProjectIssueTables: function(div, offset) {
		ajaxApi.executeAjax(offset, "GET", null)
			.done(function(data) { 
				
				var moreThan20 = false;
				if (data["meta"]["next"] != null) {
					moreThan20 = true;
				}
				var tableBody = $("#"+div+" table tbody");
				
				for (var u in data["objects"]) {
							
					var args = {};
					if (data["objects"][u]["status"]["name"] == "Closed") {
						args["class"] = "info";
					} else if (data["objects"][u]["status"]["name"] == "In Progress") {
						args["class"] = "warning";
					} else if (data["objects"][u]["status"]["name"] == "Resolved") {
						args["class"] = "success";
					} else {
						args["class"] = "error";
					}
					args["class"] = args["class"]+" event"+data["objects"][u]["id"];
					args["id"] = data["objects"][u]["id"];
					var tableRow = $("<tr />", args).appendTo(tableBody);
					$("<td />", {text: data["objects"][u]["issue_key"]}).appendTo(tableRow);
					var reporter = "";
					if (data["objects"][u]["reporter"]["first_name"] == "Anonymous") {
						reporter = data["objects"][u]["reporter"]["email"];
					} else {
						reporter = data["objects"][u]["reporter"]["first_name"] + " " + data["objects"][u]["reporter"]["last_name"];
					}
					$("<td />", {text: reporter}).appendTo(tableRow);
					var assignees = $("<td />", {});
					if (data["objects"][u]["assignees"].length == 0) {
						assignees.html("Nobody Assigned");
					} else {
						for (var a in data["objects"][u]["assignees"]) {
							$("<div />", {"text": data["objects"][u]["assignees"][a]["first_name"] + " " + data["objects"][u]["assignees"][a]["last_name"]}).appendTo(assignees);
						}
					}
					assignees.appendTo(tableRow);
					$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["pub_date"]) + " " + abrcPm.events.getTime(data["objects"][u]["pub_date"])}).appendTo(tableRow);
					$("<a />", {"text": data["objects"][u]["name"], href: "/pm/issue_details/"+data["objects"][u]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<td />", {"text": data["objects"][u]["type"]["name"]}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["status"]["name"]}).appendTo(tableRow);
					var resolution = data["objects"][u]["resolution"]["name"];
					if (resolution == "Fixed") {
						resolution += " ("+ abrcPm.events.getDate(data["objects"][u]["fixed"]) +")";
					}
					$("<td />", {"text": resolution}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["priority"]["name"]}).appendTo(tableRow);
					var iconsElement = $("<td />", {width: "35px"}).appendTo(tableRow);
					if (system._issueAssignedToMe(data["objects"][u])) {
						$("<i />", {"class": "icon-wrench"}).appendTo($("<a />", {"href": "#",
					 															"onclick": "javascript:system.editIssue("+ data["objects"][u]["id"] +")", 
					 															"data-toggle": "modal", 
					 															"data-target": "#editissue"}).appendTo(iconsElement));
						$("<i />", {"class": "icon-remove"}).appendTo($("<a />", {"href": "javascript:void(0);", "onclick": "javascript:system.deleteIssueUpdateTable("+ data["objects"][u]["id"] +")"}).appendTo(iconsElement));
					} else {
						$("<i />", {"class": "icon-question-sign"}).appendTo($("<a />", {"href": "#", "rel": "tooltip", "class": 'tip', "title": "You cannot edit this issue because it is not assigned to you."}).appendTo(iconsElement));
						
					}
				}
				
				if (moreThan20) {
					$("#more-project-issues").show('fast');
					$("#more-project-issues").off('click').on('click', function(e) {
						e.preventDefault();
						system.appendToProjectIssueTables(div, data["meta"]["next"]);
					});
				} else {
					$("#more-project-issues").hide('fast');
				}
			});
	},
	
	populateIssuesTable: function(type, which, div, mine) {
		$("#more-issues").hide();
		abrcPm.issues.filter(type, which, mine)
			.done(function(data) {
				
				var moreThan20 = false;
				if (data["meta"]["next"] != null) {
					moreThan20 = true;
				}
				
				// create a table and append it to #project-table
				var projectTableHtml = $("<table />", {"class": "table table-striped table-bordered table-hover",
													   "style": "width: 100%"});
				var tableHeaders = $("<thead />").appendTo(projectTableHtml);
				$("<th />", {"text": "Key"}).appendTo(tableHeaders);
				$("<th />", {"text": "Reporter"}).appendTo(tableHeaders);
				$("<th />", {"text": "Assignee(s)"}).appendTo(tableHeaders);
				$("<th />", {"text": "Created"}).appendTo(tableHeaders);
				$("<th />", {"text": "Project"}).appendTo(tableHeaders);
				$("<th />", {"text": "Issue"}).appendTo(tableHeaders);
				$("<th />", {"text": "Issue Type"}).appendTo(tableHeaders);
				$("<th />", {"text": "Status"}).appendTo(tableHeaders);
				$("<th />", {"text": "Resolution"}).appendTo(tableHeaders);
				$("<th />", {"text": "Priority"}).appendTo(tableHeaders);
				$("<th />", {"text": ""}).appendTo(tableHeaders);
				var tableBody = $("<tbody />").appendTo(projectTableHtml);
				var issuesExist = false;
				
				for (var u in data["objects"]) {
				
					// if this issue is assigned to me...
					if (mine) {
						if (!system._issueAssignedToMe(data["objects"][u])) {
							continue;
						} else {
							issuesExist = true;
						}
					} else {
						issuesExist = true;
					}
					
					var args = {};
					if (data["objects"][u]["status"]["name"] == "Closed") {
						args["class"] = "info";
					} else if (data["objects"][u]["status"]["name"] == "In Progress") {
						args["class"] = "warning";
					} else if (data["objects"][u]["status"]["name"] == "Resolved") {
						args["class"] = "success";
					} else {
						args["class"] = "error";
					}
					args["class"] = args["class"]+" event"+data["objects"][u]["id"];
					args["id"] = data["objects"][u]["id"];
					var tableRow = $("<tr />", args).appendTo(tableBody);
					$("<td />", {"text": data["objects"][u]["issue_key"]}).appendTo(tableRow);
					var reporter = "";
					if (data["objects"][u]["reporter"]["first_name"] == "Anonymous") {
						reporter = data["objects"][u]["reporter"]["email"];
					} else {
						reporter = data["objects"][u]["reporter"]["first_name"] + " " + data["objects"][u]["reporter"]["last_name"];
					}
					$("<td />", {text: reporter}).appendTo(tableRow);
					var assignees = $("<td />", {});
					if (data["objects"][u]["assignees"].length == 0) {
						assignees.html("Nobody Assigned");
					} else {
						for (var a in data["objects"][u]["assignees"]) {
							$("<div />", {"text": data["objects"][u]["assignees"][a]["first_name"] + " " + data["objects"][u]["assignees"][a]["last_name"]}).appendTo(assignees);
						}
					}
					assignees.appendTo(tableRow);
					$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["pub_date"]) + " " + abrcPm.events.getTime(data["objects"][u]["pub_date"])}).appendTo(tableRow);
					$("<a />", {"text": data["objects"][u]["project"]["name"], href: "/pm/project_details/"+data["objects"][u]["project"]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<a />", {"text": data["objects"][u]["name"], href: "/pm/issue_details/"+data["objects"][u]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<td />", {"text": data["objects"][u]["type"]["name"]}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["status"]["name"]}).appendTo(tableRow);
					var resolution = data["objects"][u]["resolution"]["name"];
					if (resolution == "Fixed") {
						resolution += " ("+ abrcPm.events.getDate(data["objects"][u]["fixed"]) +")";
					}
					$("<td />", {"text": resolution}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["priority"]["name"]}).appendTo(tableRow);
					var iconsElement = $("<td />", {width: "35px"}).appendTo(tableRow);
					if (system._issueAssignedToMe(data["objects"][u])) {
						$("<i />", {"class": "icon-wrench"}).appendTo($("<a />", {"href": "#",
					 															"onclick": "javascript:system.editIssue("+ data["objects"][u]["id"] +")", 
					 															"data-toggle": "modal", 
					 															"data-target": "#editissue"}).appendTo(iconsElement));
						$("<i />", {"class": "icon-remove"}).appendTo($("<a />", {"href": "javascript:void(0);", "onclick": "javascript:system.deleteIssueUpdateTable("+ data["objects"][u]["id"] +")"}).appendTo(iconsElement));
					} else {
						$("<i />", {"class": "icon-question-sign"}).appendTo($("<a />", {"href": "#", "rel": "tooltip", "class": 'tip', "title": "You cannot edit this issue because it is not assigned to you."}).appendTo(iconsElement));
						
					}
				}
		
				// if no issues exist...
				if (!issuesExist) {
					$("#"+div).html("There are no issues available");
					return;
				}
				$("#"+div).html(projectTableHtml);
				$(".tip").each(function(e) {
					$(this).tooltip({trigger: 'hover'});
				});
				
				if (moreThan20) {
					$("#more-issues").show('fast');
					$("#more-issues").off('click').on('click', function(e) {
						e.preventDefault();
						system.appendToIssueTables(div, data["meta"]["next"]);
					});
				}
			});
		
	},
	
	populateProjectIssuesTable: function(type, which, div) {
		$("#more-project-issues").hide();
		abrcPm.issues.projectFilter(type, which, window.project_id, false)
			.done(function(data) {
				
				
				var moreThan20 = false;
				if (data["meta"]["next"] != null) {
					moreThan20 = true;
				}
				
				var issuesExist = true;
				if (data["objects"].length == 0) {
					issuesExist = false;
				}
				
				// create a table and append it to #project-table
				var projectTableHtml = $("<table />", {"class": "table table-striped table-bordered table-hover",
													   "style": "width: 100%"});
				var tableHeaders = $("<thead />").appendTo(projectTableHtml);
				$("<th />", {"text": "Key"}).appendTo(tableHeaders);
				$("<th />", {"text": "Reporter"}).appendTo(tableHeaders);
				$("<th />", {"text": "Assignee(s)"}).appendTo(tableHeaders);
				$("<th />", {"text": "Created"}).appendTo(tableHeaders);
				$("<th />", {"text": "Issue"}).appendTo(tableHeaders);
				$("<th />", {"text": "Issue Type"}).appendTo(tableHeaders);
				$("<th />", {"text": "Status"}).appendTo(tableHeaders);
				$("<th />", {"text": "Resolution"}).appendTo(tableHeaders);
				$("<th />", {"text": "Priority"}).appendTo(tableHeaders);
				$("<th />", {"text": ""}).appendTo(tableHeaders);
				var tableBody = $("<tbody />").appendTo(projectTableHtml);
				
				for (var u in data["objects"]) {
					
					var args = {};
					if (data["objects"][u]["status"]["name"] == "Closed") {
						args["class"] = "info";
					} else if (data["objects"][u]["status"]["name"] == "In Progress") {
						args["class"] = "warning";
					} else if (data["objects"][u]["status"]["name"] == "Resolved") {
						args["class"] = "success";
					} else {
						args["class"] = "error";
					}
					args["class"] = args["class"]+" event"+data["objects"][u]["id"];
					args["id"] = data["objects"][u]["id"];
					var tableRow = $("<tr />", args).appendTo(tableBody);
					$("<td />", {"text": data["objects"][u]["issue_key"]}).appendTo(tableRow);
					var reporter = "";
					if (data["objects"][u]["reporter"]["first_name"] == "Anonymous") {
						reporter = data["objects"][u]["reporter"]["email"];
					} else {
						reporter = data["objects"][u]["reporter"]["first_name"] + " " + data["objects"][u]["reporter"]["last_name"];
					}
					$("<td />", {"text": reporter}).appendTo(tableRow);
					var assignees = $("<td />", {});
					if (data["objects"][u]["assignees"].length == 0) {
						assignees.html("Nobody Assigned");
					} else {
						for (var a in data["objects"][u]["assignees"]) {
							$("<div />", {"text": data["objects"][u]["assignees"][a]["first_name"] + " " + data["objects"][u]["assignees"][a]["last_name"]}).appendTo(assignees);
						}
					}
					assignees.appendTo(tableRow);
					$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["pub_date"]) + " " + abrcPm.events.getTime(data["objects"][u]["pub_date"])}).appendTo(tableRow);
					$("<a />", {"text": data["objects"][u]["name"], href: "/pm/issue_details/"+data["objects"][u]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<td />", {"text": data["objects"][u]["type"]["name"]}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["status"]["name"]}).appendTo(tableRow);
					var resolution = data["objects"][u]["resolution"]["name"];
					if (resolution == "Fixed") {
						resolution += " ("+ abrcPm.events.getDate(data["objects"][u]["fixed"]) +")";
					}
					$("<td />", {"text": resolution}).appendTo(tableRow);
					$("<td />", {"text": data["objects"][u]["priority"]["name"]}).appendTo(tableRow);
					var iconsElement = $("<td />", {"width": "35px"}).appendTo(tableRow);
					if (system._issueAssignedToMe(data["objects"][u])) {
						$("<i />", {"class": "icon-wrench"}).appendTo($("<a />", {"href": "#",
					 															"onclick": "javascript:system.editIssue("+ data["objects"][u]["id"] +")", 
					 															"data-toggle": "modal", 
					 															"data-target": "#editissue"}).appendTo(iconsElement));
						$("<i />", {"class": "icon-remove"}).appendTo($("<a />", {"href": "javascript:void(0);", onclick: "javascript:system.deleteIssueUpdateTable("+ data["objects"][u]["id"] +")"}).appendTo(iconsElement));
					} else {
						$("<i />", {"class": "icon-question-sign"}).appendTo($("<a />", {"href": "#", "rel": "tooltip", "class": 'tip', "title": "You cannot edit this issue because it is not assigned to you."}).appendTo(iconsElement));
						
					}
				}
		
				// if no issues exist...
				if (!issuesExist) {
					$("#"+div).html("There are no issues available");
					return;
				}
				$("#"+div).html(projectTableHtml);
				$(".tip").each(function(e) {
					$(this).tooltip({trigger: 'hover'});
				});
				
				if (moreThan20) {
					$("#more-project-issues").show('fast');
					$("#more-project-issues").off('click').on('click', function(e) {
						e.preventDefault();
						system.appendToProjectIssueTables(div, data["meta"]["next"]);
					});
				}
			});
		
	},
	
	populateEventsTable: function(div) {
		// create a table and append it to #project-table
		var projectTableHtml = $("<table />", {"class": "table table-striped table-bordered table-hover",
											   "style": "width: 100%"});
		var tableHeaders = $("<thead />").appendTo(projectTableHtml);
		$("<th />", {"text": "Name"}).appendTo(tableHeaders);
		$("<th />", {"text": "Start Date"}).appendTo(tableHeaders);
		$("<th />", {"text": "End Date"}).appendTo(tableHeaders);
		$("<th />", {"text": ""}).appendTo(tableHeaders);
		var tableBody = $("<tbody />").appendTo(projectTableHtml);
		
		abrcPm.events.future()
			.done(function(data) {
				if (data["objects"].length == 0) {
					$("#"+div).html("There are no events available");
					return;
				}
				for (var u = 0; u < 5; u++) {
					if (data["objects"][u] === undefined) {
						break;		// only show up to 5 events at a time.
					}
					var tableRow = $("<tr />", {"class": "event"+data["objects"][u]["id"]}).appendTo(tableBody);
					$("<a />", {"text": data["objects"][u]["name"], href: "/pm/event_details/"+data["objects"][u]["id"]+"/"}).appendTo($("<td />").appendTo(tableRow));
					$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["date"])+ " "+abrcPm.events.getTime(data["objects"][u]["date"])}).appendTo(tableRow);
					$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["end_date"])+ " "+abrcPm.events.getTime(data["objects"][u]["end_date"])}).appendTo(tableRow);
					var iconsElement = $("<span />", {"class": "dropdown"}).appendTo($("<td />", {"width": "35px"}).appendTo(tableRow));
					$("<i />", {"class": "icon-wrench"})
						.appendTo($("<a />", {"href": "#", "class": "dropdown-toggle", "data-toggle": "dropdown"})
						.appendTo(iconsElement));
						
					var dropdownElement = $("<ul />", {"class": "dropdown-menu"}).appendTo(iconsElement);
					$("<a />", 
						{"href": "#",
						 "onclick": "javascript:system.editEvent("+ data["objects"][u]["id"] +")", 
						 "data-toggle": "modal", 
						 "data-target": "#editevent", 
						 "text": "Edit Event"})
						 .appendTo($("<li />")
						 .appendTo(dropdownElement));
					$("<i />", {"class": "icon-remove"})
						.appendTo($("<a />", 
						{"href": "javascript:void(0);", 
						 "onclick": "javascript:system.deleteEventUpdateTable("+ data["objects"][u]["id"] +")"})
						.appendTo(iconsElement));
				}
				$("#"+div).html(projectTableHtml);
			});
	},
	
	populateActivityTable: function(data, div) {
		// create a table and append it to #project-table
		var projectTableHtml = $("<table />", {"class": "table table-striped table-bordered table-hover",
											   "style": "width: 100%"});
		var tableHeaders = $("<thead />").appendTo(projectTableHtml);
		$("<th />", {"text": "Activity"}).appendTo(tableHeaders);
		$("<th />", {"text": "Date"}).appendTo(tableHeaders);
		$("<th />", {"text": "Time"}).appendTo(tableHeaders);
		var tableBody = $("<tbody />").appendTo(projectTableHtml);
		if (data["objects"].length == 0) {
			$("#"+div).html("There are no activity available");
			return;
		}
		for (var u = 0; u < 5; u++) {
			if (data["objects"][u] === undefined) {
				break;		// only show up to 5 events at a time.
			}
			
			var url = "";
			if (data["objects"][u]["content_object"]["obj_type"] == "issue") {
				// get issue_details page
				url = "/pm/issue_details/"+ data["objects"][u]["content_object"]["issue_id"] +"/";
			} else if (data["objects"][u]["content_object"]["obj_type"] == "project") {
				url = "/pm/project_details/"+ data["objects"][u]["content_object"]["project_id"] +"/";
			} else if (data["objects"][u]["content_object"]["obj_type"] == "event") {
				url = "/pm/event_details/"+ data["objects"][u]["content_object"]["event_id"] +"/";
			}
			
			var tableRow = $("<tr />", {"class": "event"+data["objects"][u]["id"]}).appendTo(tableBody);
			$("<a />", {"href": url, "text": data["objects"][u]["summary"]}).appendTo($("<td />").appendTo(tableRow));
			$("<td />", {"text": abrcPm.events.getDate(data["objects"][u]["pub_date"])}).appendTo(tableRow);
			$("<td />", {"text": abrcPm.events.getTime(data["objects"][u]["pub_date"])}).appendTo(tableRow);
		}
		$("#"+div).html(projectTableHtml);
	},
	
	deleteEventUpdateTable: function(event_id) {
		if (confirm("Are you sure you want to delete?")) {
			abrcPm.events.deleteEvent(event_id).done(function(data) {
				$(".event"+event_id).hide();
			});
		}
	},
	
	deleteIssueUpdateTable: function(issue_id) {
		if (confirm("Are you sure you want to delete?")) {
			this._deleteIssueFromProjectData(issue_id);
			abrcPm.issues.deleteIssue(issue_id).done(function(data) {
				system.populateTables();
			});
		}
	},
	
	deleteProjectUpdateTable: function(project_id) {
		if (confirm("Are you sure you want to delete?")) {
			this._deleteProjectFromProjectData(project_id);
			abrcPm.projects.deleteProject(project_id).done(function(data) {
				$(".project"+project_id).hide();
				system.populateTables();
			});
		}
	},
	
	saveMe: function() {
		abrcPm.users.me().done(function(data) {
			system.me = data["objects"][0];
			$("#reporter").val(data["objects"][0]["formatted_user"]);
			$(".staff select option").filter(function() {
				return $(this).val() == data["objects"][0]["id"];
			}).attr('selected', true);
		});
	},
	
	changeSelectedProject: function(project_id) {
		$("#create-issue-project select").val(project_id);
	},
	
	addAssignee: function( issue_id ) {
		$("#newassignee").modal("show");
		abrcPm.users.generateUserDropdown("#assignee");
		
		window.assignees = [];
		
		abrcPm.issues.get(issue_id)
			.done(function(data) {
				for (var i in data["assignees"]) {
					window.assignees.push(data["assignees"][i]["id"]);
				}
				
				$("#add-assignee").off('click').click(function(e) {
					e.preventDefault();
					var newassignee = $("#assignee #user-dropdown").val();
					window.assignees.push(newassignee);
					abrcPm.issues.addAssignees(issue_id, window.assignees)
						.done(function() {
							location.reload();		
						});
							
				});
			});
	},
	
	addWatcher: function(issue_id) {
		$("#newwatcher").modal("show");
		abrcPm.users.generateUserDropdown("#watcher");
		
		window.watchers = [];
		
		abrcPm.issues.get(issue_id)
			.done(function(data) {
				for (var i in data["watchers"]) {
					window.watchers.push(data["watchers"][i]["id"]);
				}
				
				$("#add-watcher").off('click').click(function(e) {
					e.preventDefault();
					var newwatcher = $("#watcher #user-dropdown").val();
					window.watchers.push(newwatcher);
					abrcPm.issues.addWatchers(issue_id, window.watchers)
						.done(function(data) {
							location.reload();		
						});		
				});
			});
	},
	
	createSearchWordTable: function(project_id) {
		
		abrcPm.search.getSearchWords(project_id)
			.done(function(data) {
				var div = "#searchWordsTable";
				var searchWordsTableHtml = $("<table />", {"class": "table table-striped table-bordered table-hover",
													   	   "style": "width:100%"});
				var tableHeaders = $("<thead />").appendTo(searchWordsTableHtml);
				$("<th />", {"text": "Search Word"}).appendTo(tableHeaders);
				$("<th />", {"text": ""}).appendTo(tableHeaders);
				var tableBody = $("<tbody />", {"id": "word"}).appendTo(searchWordsTableHtml);
				if (data["objects"].length == 0) {
					$(div).html("There are no search words available");
					return;
				}
				
				for (var word in data["objects"]) {
					var searchWord = data["objects"][word]["word"];
					
					var tableRow = $("<tr />").appendTo(tableBody);
					
					$("<td />", {"text": searchWord}).appendTo(tableRow);
					$("<i />", {"class": "icon-remove"})
						.appendTo($("<a />", {"href": "javascript:void(0);", 
											  "onclick": "system.deleteWord("+ data["objects"][word]["id"] +", "+ project_id +")"})
						.appendTo($("<td />").appendTo(tableRow)));
				}
				
				$(div).html(searchWordsTableHtml);
			});
			
		$("#addNewWordLink").off('click').on('click', function(e) {
			
			e.preventDefault();
			
			system.newWord(project_id);
		});
		
	},
	
	deleteWord: function(word_id, project_id) {
		abrcPm.search.deleteWord(word_id)
			.done(function(data) {
				system.createSearchWordTable(project_id);
			});
	},
	
	newWord: function(project_id) {
		$("#newWord").show();
		
		$("#addNewWordBtn").off('click').on('click', function(e) {
			
			var word = $("#newWordText").val();
			
			abrcPm.search.addWord(word, project_id)
				.done(function(data) {
					system.createSearchWordTable(project_id);
					$("#newWord").hide();
					$("#newWordText").val("");
				});
		});
	},
	
	deleteWatcher: function(issue_id, user_id) {
		abrcPm.issues.get(issue_id)
			.done(function(data) {
				watchers = [];
				
				for (var i in data["watchers"]) {
					if (!(data["watchers"][i]["id"] == user_id)) {
						watchers.push(data["watchers"][i]["id"]);
					}
				}
				
				abrcPm.issues.addWatchers(issue_id, watchers)
					.done(function() {
						$("#watcher"+user_id).hide();
					});
					
			});
	},
	
	deleteAssignee: function(issue_id, user_id) {
		abrcPm.issues.get(issue_id)
			.done(function(data) {
				assignees = [];
				
				for (var i in data["assignees"]) {
					if (!(data["assignees"][i]["id"] == user_id)) {
						assignees.push(data["assignees"][i]["id"]);
					}
				}
				
				abrcPm.issues.addAssignees(issue_id, assignees)
					.done(function() {
						$("#assignee"+user_id).hide();
					});
					
			});
	},
	
	showAttachmentAddFiles: function() {
		$("#attachment-add-files").show('fast');
	},
	
	_deleteIssueFromProjectData: function(issue_id) {
		$("#"+issue_id).hide('fast');
	},
	
	_deleteProjectFromProjectData: function(project_id) {
		var data = this.projectData;
		for (var p in data["objects"]) {
			if (data["objects"][p]["id"] == project_id) {
				delete data["objects"][p];
			}
		}
	},
	
	_issueAssignedToMe: function(issue) {
		
		if (system.me.id === issue["project"]["lead"]["id"]) {
			return true;
		}
		
		if (system.me.id === issue["reporter"]["id"]) {
			return true;
		}
		
		for (var i in issue["assignees"]) {
			if (system.me.id === issue["assignees"][i]["id"]) {
				return true;
			}
		}
		return false;
	},
	
	_emailStaffOnly: function() {
		if(jQuery("#email_staff").is("input[type=checkbox]")) {
	        if(jQuery("#email_staff").is(":checked")) {
	            return true;
	        } else {
	            return false;
	        }
	    }
	}
};
var system = null;
$(function() {system = abrcPmSystem().init();});
