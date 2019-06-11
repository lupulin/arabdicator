/**
 * ABRC API Client for ABRC websites.
 * 
 * Create an easy-to-use interface to the entire ABRC API.
 * 
 * One caveat: 
 * 
 * All API calls must be authenticated/authorized somehow. Also,
 * POST calls must be CSRF token protected and API must not be allowed to be
 * called cross domain.
 * 
 * Easy data formatter JS library for ABRC API. 
 * 
 * Recommended operations:
 * 
 * 1. Make sure that any dropdown box has a value of the unique ID of the data.
 * 2. Each function represents an AJAX call for each of the available methods / model.
 * 3. Do something like this: 
 * 			- AbrcPm.acceptUserRequest(user_id);
 * 			- AbrcPm.createComment(comment, my_user_id, issue_id);
 * 			- AbrcPm.createIssue(name, description, my_user_id, project_id, issueType_id, resolution_id, priority_id);
 * 			- AbrcPm.createProject(name, description, key, reporter_id);
 * 			- AbrcPm.generateIssueTypeDropdown();
 * 			- AbrcPm.generateResolutionDropdown();
 * 			- AbrcPm.generateUserDropdown();
 * 			- ...
 * 			- ...
 * 			- etc...
 * 
 * REQUIRES: jQuery, json2
 * 
 * @author: Chris Bartos <bartos.25@osu.edu>
 */

function SimpleAjax() {
	if (this === window) {
		return new SimpleAjax();
	} else {
		return this;
	}
}

function AbrcPm() {
	if (this === window) {
		return new AbrcPm();
	} else {
		return this;
	}
}

SimpleAjax.prototype = {
	
	baseUrl: "/pm/v1/",
	
	defaultApp: "pm/",
	
	/**
	 * Our "constructor".
	 * 
	 * This is used to initialize our AJAX settings among any other
	 * thing that we might need in order to use our AJAX library.
	 */
	init: function() {
		
		return this;
	},
	
	/**
	 * The base directory is the path to the API.
	 * 
	 * In this JS library the default path to the API
	 * is: /api/v1/pm/
	 */
	getBaseDir: function() {
		return this.baseUrl + this.defaultApp;
	},
	
	/**
	 * Determine the methods that are considered CSRF safe.
	 * 
	 * It turns out that POST requests are the only requests that
	 * require a CSRF token. But, if the CSRF token is not needed
	 * by the system, it can simply ignore it. CSRF token provides
	 * some extra safety.
	 * 
	 * @param {Object} method
	 */
	csrfSafeMethod: function(method) {
		// these HTTP methods do not require CSRF protection
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	},
	
	/**
	 * Determines if the url that we are requesting in AJAX
	 * is of the same origin.
	 * 
	 * Same origin means that the protocol, domain, and port
	 * are all the same.
	 * 
	 * http://localhost:8000/ is not the same as:
	 * http://127.0.0.1:8000/
	 * 
	 * localhost !== 127.0.0.1
	 * 
	 * @param {Object} url
	 */
	sameOrigin: function(url) {
		// test that a given url is a same-origin URL
		// url could be relative or scheme relative or absolute
		var host = document.location.host;
		var protocol = document.location.protocol;
		var sr_origin = "//" + host;
		var origin = protocol + sr_origin;
		
		// Allow absolute or scheme relative URLs to same origin
		return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
			(url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
			// or any other URL that isn't scheme relative or absolute i.e. relative
			!(/^(\/\/\|http:|https:).*/.test(url));
	},
	
	/**
	 * Returns the value of a cookie. Used specifically for attaining the
	 * CSRF Token cookie so that we can append it to a POST request in 
	 * jQuery $.ajax() calls.
	 *  
 	 * @param {Object} name
	 */
	getCookie: function(name) {
		var cookieValue = null;
	    if (document.cookie && document.cookie != '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	},
	
	/**
	 * Executes our AJAX request.
	 * 
	 * Automatically stringify's the data that we are going to pass in.
	 * Also, automatically will append headers: "X-HTTP-Method-Override",
	 * if the requested method is not supported by the browser.
	 * 
 	 * @param {Object} data
 	 * @param {Object} type
 	 * @param {Object} path
	 */
	executeAjax: function(path, type, data, username, api_key) {
		var urlPath = path;
		if (urlPath.indexOf(this.getBaseDir()) == -1) { 
			urlPath = this.getBaseDir()+path 
		}
		var ajaxData = {
			url: urlPath,
			contentType: 'application/json',
			dataType: 'json',
			processData: false,
			headers: {}
		};
		var encodedData = JSON.stringify(data);
		if (type == "GET") {
			ajaxData.type = "GET";
		} else if (type == "POST") {
			ajaxData.type = "POST";
			ajaxData.data = encodedData;
		} else {
			ajaxData.type = "POST";
			ajaxData.data = encodedData;
			ajaxData.headers["X-HTTP-Method-Override"] = type;
		}
		
		if (username && api_key) {
			ajaxData.headers["Authorization"] = "ApiKey " + username +":"+api_key;
		}
		
		return $.ajax(ajaxData);
	}
};
var ajaxApi = SimpleAjax();

$(function() {
	// AJAX settings
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!ajaxApi.csrfSafeMethod(settings.type) && ajaxApi.sameOrigin(settings.url)) {
				// Send the token to same-origin, relative URLs only.
				// Send the token only if the method warrants CSRF protection
				// Using the CSRFToken value acquired earlier
				xhr.setRequestHeader("X-CSRFToken", ajaxApi.getCookie('csrftoken'));
			}
		},
		cache: false
	});
	
	$(".modal").draggable({
	    handle: ".modal-header"
	});
	
	// Modal settings
	$('.modal').modal({
        backdrop: true,
        keyboard: true,
        show: false
    }).css({
        'width': 'auto',
        'margin-top': function() {
        	return -($(this).height() / 1.5);
        },
        'margin-left': function () {
            return -($(this).width() / 2);
        }
    });
    
    $(".modal-body").css({
    	'overflow-y': 'scroll',
    	'max-height': "100%"
    });
    
    $('input, textarea').placeholder();
});

AbrcPm.prototype = {
	
	search: {
		
		getSearchWords: function(project_id) {
			return ajaxApi.executeAjax('words/?project='+project_id, "GET", null)
		},
		
		addWord: function(word, project_id) {
			var wordData = {
				"word": word,
				"project": ajaxApi.getBaseDir()+"project/"+project_id+"/"
			};
			
			return ajaxApi.executeAjax('words/', "POST", wordData);
		},
		
		deleteWord: function(word_id) {
			return ajaxApi.executeAjax('words/'+word_id+'/', "DELETE", null);
		}
		
	},
	
	projects: {
		/**
		 * Returns all the projects that have been created in the past
		 */
		all: function() {
			return ajaxApi.executeAjax('project/', "GET", null)
		},
		
		/**
		 * Deletes a project simply using a project ID
		 *  
	 	 * @param {Object} proj_id
		 */
		deleteProject: function(proj_id) {
			return ajaxApi.executeAjax('project/'+proj_id+'/', "DELETE", null);
		},
		
		get: function(project_id) {
			return ajaxApi.executeAjax('project/'+project_id+'/', "GET", null);
		},
		
		/**
		 * Add a new project using name, description, key, and lead_id
		 * 
		 * @param {Object} name
 		 * @param {Object} description
 		 * @param {Object} key
 		 * @param {Object} lead_id
		 */
		add: function(name, description, key, lead_id) {
			var projData = {
				"name": name,
				"description": description,
				"key": key,
				"lead": ajaxApi.getBaseDir()+"user/"+lead_id+"/"
			};
			return ajaxApi.executeAjax('project/', "POST", projData);
		},
		
		/**
		 * Edit a project using project ID and all the available data.
		 *  
 		 * @param {Object} proj_id
 		 * @param {Object} name
 		 * @param {Object} description
 		 * @param {Object} key
 		 * @param {Object} lead_id
		 */
		edit: function(proj_id, name, description, key, lead_id) {
			var projData = {
				"name": name,
				"description": description,
				"key": key,
				"lead": ajaxApi.getBaseDir()+"user/"+lead_id+"/"
			};
			return ajaxApi.executeAjax('project/'+proj_id+'/', "PUT", projData);
		},
		
		/**
		 * Change the description using the project_id
		 *  
 		 * @param {Object} proj_id
 		 * @param {Object} description
		 */
		changeDescription: function(proj_id, description) {
			var projData = {
				"description": description
			};
			return ajaxApi.executeAjax('project/'+proj_id+'/', "PATCH", projData);
		},
		
		/**
		 * Change the lead using the lead_id and project id
		 *  
 		 * @param {Object} proj_id
 		 * @param {Object} lead_id
		 */
		changeLead: function(proj_id, lead_id) {
			var projData = {
				"lead": ajaxApi.getBaseDir()+"user/"+lead_id+"/"
			};
			return ajaxApi.executeAjax('project/'+proj_id+'/', "PATCH", projData);
		},
		
		/**
		 * Change the project name using project id
		 *  
 		 * @param {Object} proj_id
 		 * @param {Object} name
		 */
		changeName: function(proj_id, name) {
			var projData = {
				"name": name
			};
			return ajaxApi.executeAjax('project/'+proj_id+'/', "PATCH", projData);
		},
		
		/**
		 * Change the project key with a project id
		 *  
 		 * @param {Object} proj_id
 		 * @param {Object} key
		 */
		changeKey: function(proj_id, key) {
			var projData = {
				"key": key
			};
			return ajaxApi.executeAjax('project/'+proj_id+'/', "PATCH", projData);
		},
		
		generateProjectDropdown: function(div, defaultSelect) {
			if (defaultSelect === null || defaultSelect === undefined) {
				defaultSelect = 1;
			}
			ajaxApi.executeAjax('project/', "GET", null)
				.done(function(data) {
					var select = $('<select />');
					for (var u in data["objects"]) {
						var d = {
							"value": data["objects"][u]["id"], 
							"text": data["objects"][u]["name"]
						}
						if (data["objects"][u]["id"] == defaultSelect) {
							d["selected"]="selected";
						}
						
						$('<option />', d).appendTo(select);			
					}
					$(div).html(select);
					
				});
		}
	},
	
	issues: {
		/**
		 * Returns all the issues that have been created in the past
		 */
		all: function(mine) {
			if (mine) {
				return abrcPm.issues.allMine();
			} else {
				return ajaxApi.executeAjax('issue/', "GET", null);
			}
		},
		
		allMine: function() {
			return ajaxApi.executeAjax('assigned/', "GET", null);
		},
		
		userIssues: function(user_id) {
			return ajaxApi.executeAjax('issue/?user='+user_id, "GET", null);
		},
		
		/**
		 * Deletes a project simply using a issue ID
		 *  
	 	 * @param {Object} issue_id
		 */
		deleteIssue: function(issue_id, api_key, username) {
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "DELETE", null);
		},
		
		/**
		 * Add a new issue using name, description, resolution, priority, type, status, and report id
		 * 
		 * @param {Object} name
 		 * @param {Object} description
 		 * @param {Object} resolution
 		 * @param {Object} priority
 		 * @param {Object} type
 		 * @param {Object} status
 		 * @param {Object} report_id
		 */
		add: function(name, proj_id, description, resolution_id, priority_id, issue_type_id, status_id, reporter_id) {
			var issueData = {
				"name": name,
				"description": description,
				"project": ajaxApi.getBaseDir()+"project/"+proj_id+"/",
				"resolution": ajaxApi.getBaseDir()+"resolution/"+resolution_id+"/",
				"priority": ajaxApi.getBaseDir()+"priority/"+priority_id+"/",
				"type": ajaxApi.getBaseDir()+"issuetype/"+issue_type_id+"/",
				"status": ajaxApi.getBaseDir()+"status/"+status_id+"/",
				"reporter": ajaxApi.getBaseDir()+"user/"+reporter_id+"/"
			};
			return ajaxApi.executeAjax('issue/', "POST", issueData);
		},
		
		myAssigned: function(user_id, mine) {
			var url = "issue/";
			if (mine) { url = "assigned/"}
			return ajaxApi.executeAjax(url+'?assignees__in='+user_id, "GET", null);
		},
		
		myReported: function(user_id, mine) {
			var url = "issue/";
			if (mine) { url = "assigned/"}
			return ajaxApi.executeAjax(url+'?reporter='+user_id, "GET", null);
		},
		
		search: function(search, mine) {
			var url = "issue/";
			if (mine) { url = "assigned/"}
			return ajaxApi.executeAjax(url+'?query='+search, "GET", null);
		},
		
		projectSearch: function(search, project_id, mine) {
			var url = "issue/";
			if (mine) { url = "assigned/"}
			
			return ajaxApi.executeAjax(url+'?query='+search+"&project="+project_id, "GET", null);
		},
		
		projectFilter: function(filter_type, filter_num, project_id, mine) {
			var url = "issue/";
			if (mine) { url = "assigned/"}
			var projectSearch = "project="+project_id;
			if (filter_type == "search") {
				return abrcPm.issues.projectSearch(filter_num, project_id, mine);
			} else if (filter_type == "assigned") {
				return abrcPm.issues.myAssigned(filter_num+"&"+projectSearch, mine);
			} else if (filter_type == "reported") {
				return abrcPm.issues.myReported(filter_num+"&"+projectSearch, mine);
			} else if (filter_type != "all") {
				projectSearch += "&"+filter_type+"="+filter_num
			}
			return ajaxApi.executeAjax(url+'?'+projectSearch, 'GET', null);
		},
		
		filter: function(filter_type, filter_num, mine) {
			var url = "issue/";
			if (mine) { url = "assigned/"}
			if (filter_type == "all") {
				return abrcPm.issues.all(mine);
			} else if (filter_type == "search") {
				return abrcPm.issues.search(filter_num, mine);
			} else if (filter_type == "assigned") {
				return abrcPm.issues.myAssigned(filter_num, mine);
			} else if (filter_type == "reported") {
				return abrcPm.issues.myReported(filter_num, mine);
			} else if (filter_type == "user") {
				return abrcPm.issues.userIssues(filter_num);
			} else {
				return ajaxApi.executeAjax(url+'?'+filter_type+"="+filter_num, "GET", null);
			}
		},
		
		get: function(issue_id, issue_name) {
			if (issue_name == null || issue_name == undefined) {			
				return ajaxApi.executeAjax('issue/'+issue_id+'/', "GET", null);
			} else {
				return ajaxApi.executeAjax('issue/?name__exact='+issue_name, "GET", null);
			}
		},
		
		getAssigned: function(issue_id) {
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "GET", null);
		},
		
		/**
		 * Edit a project using project ID and all the available data.
		 * 
		 *  - Assignees and watchers same people
		 *  - Emails automatically create issue (save email, non-active user)
		 *
		 *  - Help Desk (orders, invoices, donations, shipping)
		 * 	- Technical (sequences, primer, inserts, t-dna)
		 *  - Education (education, trained, greening the classroom)
		 *  - Miscellaneous
		 * 
		 *  - Disable emails for "vacation"
		 *  - Change project manager for a project
		 * 
		 *  - Filter by status, date
		 *  - Current comments at top
		 *  - Search keyword in entire issue
		 * 
		 *  - Allow Forwarded emails
		 * 
		 * @param {Object} issue_id
 		 * @param {Object} name
 		 * @param {Object} description
 		 * @param {Object} resolution
 		 * @param {Object} priority
 		 * @param {Object} type
 		 * @param {Object} status
 		 * @param {Object} report_id
		 */
		edit: function(issue_id, proj_id, name, description, resolution_id, priority_id, issue_type_id, status_id, reporter_id) {
			var issueData = {
				"name": name,
				"description": description,
				"project": ajaxApi.getBaseDir()+"project/"+proj_id+"/",
				"resolution": ajaxApi.getBaseDir()+"resolution/"+resolution_id+"/",
				"priority": ajaxApi.getBaseDir()+"priority/"+priority_id+"/",
				"type": ajaxApi.getBaseDir()+"issuetype/"+issue_type_id+"/",
				"status": ajaxApi.getBaseDir()+"status/"+status_id+"/",
				"reporter": ajaxApi.getBaseDir()+"user/"+reporter_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		projectIssues: function(project_id) {
			return ajaxApi.executeAjax('issue/?project='+project_id, "GET", null);
		},
		
		changeProject: function(issue_id, proj_id) {
			var issueData = {
				"project": ajaxApi.getBaseDir()+"project/"+proj_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changeName: function(issue_id, name) {
			var issueData = {
				"name": name
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changeDescription: function(issue_id, description) {
			var issueData = {
				"description": description
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changeResolution: function(issue_id, resolution_id) {
			var issueData = {
				"resolution": ajaxApi.getBaseDir()+"resolution/"+resolution_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changePriority: function(issue_id, priority_id) {
			var issueData = {
				"priority": ajaxApi.getBaseDir()+"priority/"+priority_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changeIssueType: function(issue_id, issue_type_id) {
			var issueData = {
				"type": ajaxApi.getBaseDir()+"issuetype/"+issue_type_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changeStatus: function(issue_id, status_id) {
			var issueData = {
				"status": ajaxApi.getBaseDir()+"status/"+status_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		changeReporter: function(issue_id, reporter_id) {
			var issueData = {
				"reporter": ajaxApi.getBaseDir()+"user/"+reporter_id+"/"
			};
			return ajaxApi.executeAjax('assigned/'+issue_id+'/', "PATCH", issueData);
		},
		
		addAssignees: function(issue_id, assignees) {
			var assigneeArray = [];
			for (var i in assignees) {
				assigneeArray.push(ajaxApi.getBaseDir()+"user/"+assignees[i]+"/");
			}
			var issueData = {
				"assignees": assigneeArray
			};
			return ajaxApi.executeAjax("issue/"+issue_id+'/', "PATCH", issueData);
		},
		
		addWatchers: function(issue_id, watchers) {
			var watcherArray = [];
			for (var i in watchers) {
				watcherArray.push(ajaxApi.getBaseDir()+"user/"+watchers[i]+"/");
			}
			var issueData = {
				"watchers": watcherArray
			};
			return ajaxApi.executeAjax("issue/"+issue_id+'/', "PATCH", issueData);
		},
		
		/**
		 * @deprecated -- 
		 * generateIssueTypeDropdown will be removed from abrcPM because it simply
		 * doesn't makes sense being here.
		 * 
		 *  
		 * @param {Object} div
		 * @param {Object} defaultSelect
		 */
		generateIssueTypeDropdown: function(div, defaultSelect) {
			if (defaultSelect === null || defaultSelect === undefined) {
				defaultSelect = 4;
			}
			ajaxApi.executeAjax('issuetype/', "GET", null)
				.done(function(data) {
					var select = $('<select />', {"id": "issue-type-dropdown"});
					for (var u in data["objects"]) {
						
						var d = {
							"value": data["objects"][u]["id"], 
							"text": data["objects"][u]["name"]
						}
						if (data["objects"][u]["id"] == defaultSelect) {
							d["selected"]="selected";
						}
						
						$('<option />', d).appendTo(select);		
					}
					$(div).html(select);
					
				});
		},
		
		/**
		 * @deprecated -- 
		 * generateStatusDropdown will be removed from abrcPM because it simply
		 * doesn't makes sense being here.
		 * 
		 *  
		 * @param {Object} div
		 * @param {Object} defaultSelect
		 */
		generateStatusDropdown: function(div, defaultSelect) {
			if (defaultSelect === null || defaultSelect === undefined) {
				defaultSelect = 1;
			}
			ajaxApi.executeAjax('status/', "GET", null)
				.done(function(data) {
					var select = $('<select />');
					for (var u in data["objects"]) {
						var d = {
							"value": data["objects"][u]["id"], 
							"text": data["objects"][u]["name"]
						}
						if (data["objects"][u]["id"] == defaultSelect) {
							d["selected"]="selected";
						}
						
						$('<option />', d).appendTo(select);			
					}
					$(div).html(select);
					
				});
		},
		
		/**
		 * @deprecated -- 
		 * generatePriorityDropdown will be removed from abrcPM because it simply
		 * doesn't makes sense being here.
		 * 
		 *  
		 * @param {Object} div
		 * @param {Object} defaultSelect
		 */
		generatePriorityDropdown: function(div, defaultSelect) {
			if (defaultSelect === null || defaultSelect === undefined) {
				defaultSelect = 4;
			}
			ajaxApi.executeAjax('priority/', "GET", null)
				.done(function(data) {
					var select = $('<select />');
					for (var u in data["objects"]) {
						var d = {
							"value": data["objects"][u]["id"], 
							"text": data["objects"][u]["name"]
						}
						if (data["objects"][u]["id"] == defaultSelect) {
							d["selected"]="selected";
						}
						
						$('<option />', d).appendTo(select);			
					}
					$(div).html(select);
					
				});
		},
		
		/**
		 * @deprecated -- 
		 * generateResolutionDropdown will be removed from abrcPM because it simply
		 * doesn't makes sense being here.
		 * 
		 *  
		 * @param {Object} div
		 * @param {Object} defaultSelect
		 */
		generateResolutionDropdown: function(div, defaultSelect) {
			if (defaultSelect === null || defaultSelect === undefined) {
				defaultSelect = 1;
			}
			ajaxApi.executeAjax('resolution/', "GET", null)
				.done(function(data) {
					var select = $('<select />');
					for (var u in data["objects"]) {
						var d = {
							"value": data["objects"][u]["id"], 
							"text": data["objects"][u]["name"]
						}
						if (data["objects"][u]["id"] == defaultSelect) {
							d["selected"]="selected";
						}
						
						$('<option />', d).appendTo(select);			
					}
					$(div).html(select);
					
				});
		}
	},
	
	templates: {
		add: function(name, template) {
			var templateData = {
				"name": name,
				"template": template
			};
			return ajaxApi.executeAjax('template/', "POST", templateData);
		},
		
		all: function() {
			return ajaxApi.executeAjax('template/', "GET", null);
		},
		
		deleteTemplate: function(template_id) {
			return ajaxApi.executeAjax('template/'+ template_id +'/', "DELETE", null);
		},
		
		edit: function(template_id, name, template) {
			var templateData = {
				"name": name,
				"template": template
			};
			return ajaxApi.executeAjax('template/'+ template_id + '/', "PUT", templateData);
		},
		
		get: function(template_id) {
			return ajaxApi.executeAjax('template/'+ template_id +'/', "GET", null);
		},
		
		generateTemplateDropdown: function(div) {
			
			$(div).html("");
			
			abrcPm.templates.all()
				.done(function(data) {
					var select = $(div);
					var templateData = {
						value: -1,
						text : "Select a Template"
					};
					
					$("<option />", templateData).appendTo(select);
					
					for (var u in data["objects"]) {
						var templateData = {
							value: data["objects"][u]["id"],
							text : data["objects"][u]["name"]
						};
						
						$("<option />", templateData).appendTo(select);
					}
					
					$(div).off('change').on('change', function(e) {
				
						e.preventDefault();
						
						var dropdownVal = $("#template-dropdown").val();
						
						abrcPm.templates.get(dropdownVal)
							.done(function(data) {
								$("#create-comment-text").val(data["template"]);
							});
					});
				});
				
		}
	},
	
	comments: {
		
		all: function() {
			return ajaxApi.executeAjax('comment/', "GET", null);
		},
		
		add: function(issue_id, comment, commenter_id, just_staff) {
			
			var commentData = {
				"issue": ajaxApi.getBaseDir()+"issue/"+issue_id+"/",
				"comment": comment,
				"commenter": ajaxApi.getBaseDir()+"user/"+commenter_id+"/",
				"only_staff": just_staff
			};
			return ajaxApi.executeAjax('comment/', "POST", commentData);
		},
		
		get: function(comment_id) {
			return ajaxApi.executeAjax('comment/'+comment_id+'/', "GET", null);
		},
		
		deleteComment: function(comment_id) {
			return ajaxApi.executeAjax('comment/'+comment_id+'/', "DELETE", null);
		},
		
		edit: function(comment_id, comment) {
			var commentData = {
				"comment": comment
			};
			return ajaxApi.executeAjax('comment/'+comment_id+'/', "PATCH", commentData);
		}
		
	},
	
	users: {
		
		requestInvitation: function(email, first_name, last_name) {
			var inviteData = {
				"firstname": first_name,
				"lastname": last_name,
				"email": email
			};
			return ajaxApi.executeAjax('request/', "POST", inviteData);
		},
		
		emailExists: function(email) {
			
		},
		
		edit: function(user_id, first_name, last_name, username, email, password) {
			var userData = {
				"first_name": first_name,
				"last_name": last_name,
				"username": username,
				"email": email,
				"password": password
			};
			return ajaxApi.executeAjax('user/'+user_id+"/", "PUT", userData);
		},
		
		profileEdit: function(user_id, first_name, last_name, username, email) {
			var userData = {
				"first_name": first_name,
				"last_name": last_name,
				"username": username,
				"email": email
			};
			return ajaxApi.executeAjax('user/'+user_id+"/", "PATCH", userData);
		},
		
		acceptInvitationRequest: function(invite_id) {
			var inviteData = {
				"accepted": true
			};
			return ajaxApi.executeAjax('invite/'+invite_id+'/', "PATCH", inviteData);
		},
		
		rejectInvitationRequest: function(invite_id) {
			return ajaxApi.executeAjax('invite/'+invite_id+'/', "DELETE", null);
		},
		
		getInvitations: function() {
			return ajaxApi.executeAjax('/invite/?accepted=false', "GET", null);
		},
		
		add: function(first_name, last_name, username, email, password) {
			var userData = {
				"first_name": first_name,
				"last_name": last_name,
				"username": username,
				"email": email,
				"password": password
			};
			return ajaxApi.executeAjax('usercreate/', "POST", userData);
		},
		
		me: function() {
			return ajaxApi.executeAjax('me/', 'GET', null);
		},
		
		get: function(user_id) {
			return ajaxApi.executeAjax('user/'+user_id+'/', "GET", null);
		},
		
		deleteUser: function(user_id) {
			return ajaxApi.executeAjax('user/'+user_id+'/', "DELETE", null);
		},
		
		deleteAll: function() {
			return ajaxApi.executeAjax('invite/', "DELETE", null);
		},
		
		/**
		 * @deprecated --
		 * generateUserDropdown will be removed from abrcPM due to the fact that 
		 * it makes no sense being in here.
		 * 
		 * @param {Object} div
		 * @param {Object} user_id
		 */
		generateUserDropdown: function(div, user_id) {
			
			return ajaxApi.executeAjax('staff/', "GET", null).done(function(data) {
				var select = $('<select />', {id: "user-dropdown"});
				for (var u in data["objects"]) {
					
					var userData = {"value": data["objects"][u]["id"], 
									"text": data["objects"][u]["formatted_user"]};
						
					if (user_id != null || user_id != undefined) {
						if (user_id == data["objects"][u]["id"]) {
							userData["selected"] = "selected";
						}
					}
					
					$('<option />', userData).appendTo(select);
				
					
				}
				$(div).html(select);
				
			});
		}
	},
	
	emailserver: {
		all: function() {
			return ajaxApi.executeAjax('emailserver/', 'GET', null);
		},
		
		edit: function(id, name, host, email, port, username, password) {
			var serverData = {
				"name": name,
				"hostname": host,
				"email": email,
				"port": port,
				"username": username,
				"password": password
			};
			return ajaxApi.executeAjax('emailserver/'+id+"/", 'PUT', serverData);
		}
	},
	
	activity: {
		all: function() {
			return ajaxApi.executeAjax('activity/', 'GET', null);
		}
	},
	
	events: {
		
		all: function() {
			return ajaxApi.executeAjax('event/', "GET", null);
		},
		
		future: function() {
			var date = new Date().toJSON();
			return ajaxApi.executeAjax('event/?date__gte='+date, "GET", null);
		},
		
		past: function() {
			var date = new Date().toJSON();
			return ajaxApi.executeAjax('event/?date__lte='+date, "GET", null);
		},
	
		get: function(event_id) {
			return ajaxApi.executeAjax('event/'+event_id+'/', "GET", null);
		},
		
		addAttendee: function(event_id, attendees) {
			var attendeeData = {
				"attendees": attendees
			};
			return ajaxApi.executeAjax('event/'+event_id+'/', "PATCH", attendeeData);
		},
		
		edit: function(event_id, eventName, eventDesc, eventLoca, startEventDate, endEventDate) {
			var eventData = {
				"name": eventName,
				"description": eventDesc,
				"location": eventLoca,
				"date": startEventDate,
				"end_date": endEventDate
			};
			return ajaxApi.executeAjax('event/'+event_id+'/', "PUT", eventData);
		},
		
		add: function(eventName, eventDesc, eventLoca, startEventDate, endEventDate) {
			var eventData = {
				"name": eventName,
				"description": eventDesc,
				"location": eventLoca,
				"date": startEventDate,
				"end_date": endEventDate
			};
			return ajaxApi.executeAjax('event/', "POST", eventData);
		},
		
		deleteEvent: function(event_id) {
			return ajaxApi.executeAjax('event/'+event_id+'/', "DELETE", null);
		},
		
		/**
		 * @deprecated
		 *  
 		 * @param {Object} date
		 */
		getDate: function(date) {
		    var time = moment(date.replace('T', ' '))
		    return time.format('MM/DD/YYYY');
		},
		
		/**
		 * @deprecated
		 *  
 		 * @param {Object} date
		 */
		getTime: function(date) {
			var wholeDate = date.split('T');
			var time = moment(date.replace('T', ' '));
			if (wholeDate[1] == "11:11:11") {
				return "all day";
			} else {
				return time.format("LT");
			}
			
		},
		
		/**
		 * @deprecated
		 *  
 		 * @param {String} date
		 */
		unformatDate: function(date) {
			dateTime = date.split("T");
			patt = /\d{4}-\d{1,2}-\d{1,2}/;
			if (!patt.test(dateTime[0])) {
				return;
			}
			d = dateTime[0].split('-');
			return d[1] + '/' + d[2] + '/' + d[0] + ' ' + dateTime[1].slice(0, 5);
		},
		
		/**
		 * @deprecated
		 *  
 		 * @param {String} date
		 */
		formatDate: function(date) {
			dateTime = date.split(" ");
			patt = /\d{1,2}\/\d{1,2}\/\d{4}/;
			if (!patt.test(dateTime[0])) {
				return;
			}
			d = dateTime[0].split('/');
			return d[2] + '-' + ('0'+d[0]).slice(-2) + '-' + ('0'+d[1]).slice(-2) + "T" + dateTime[1] + ":00";
		}
		
	}
	
};
var abrcPm  = AbrcPm();
