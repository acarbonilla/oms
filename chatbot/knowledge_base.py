"""
Knowledge base for OMS-specific information
"""

from .database_service import db_service

OMS_KNOWLEDGE_BASE = {
    "dashboard": {
        "description": "Main dashboard overview and navigation",
        "features": [
            "View facility statistics",
            "Recent activities overview",
            "Quick access to main features",
            "Regional data summary",
            "User activity tracking"
        ],
        "common_questions": {
            "what_can_i_see": "The dashboard shows facility counts, recent technical activities, pending assessments, and quick links to all main features based on your role and region.",
            "how_to_navigate": "Use the main navigation menu to access Facilities, Technical Activities, Quality Assessment, and Reports sections. Your permissions determine what you can see.",
            "what_are_stats": "Dashboard statistics include total facilities, QR code coverage, recent activities, risk levels, and pending evaluations.",
            "how_to_refresh": "Dashboard data updates automatically. You can refresh by clicking your browser refresh button or navigating back to the home page."
        }
    },
    
    "facility_management": {
        "description": "Facility management system for tracking and managing facilities",
        "features": [
            "Create new facilities",
            "QR code generation for facilities",
            "Facility status tracking",
            "Location management",
            "Image upload and comparison",
            "View facility list",
            "Search and filter facilities",
            "Edit facility details"
        ],
        "user_groups": ["AM", "EMP", "EV"],
        "urls": {
            "main": "/facility-management/",
            "create": "/facility-management/create/",
            "list": "/facility-management/list/",
            "qr_generation": "/facility-management/qr-generate/",
            "tracking": "/facility-management/track/"
        },
        "how_to": {
            "create_facility": [
                "1. Click 'Facility Management' in the menu",
                "2. Select 'Create New Facility'",
                "3. Fill in required fields: Name, Location, Region",
                "4. Add description and details",
                "5. Click 'Save'",
                "6. Optionally generate QR code for the facility"
            ],
            "generate_qr": [
                "1. Go to Facility Management",
                "2. Find your facility in the list",
                "3. Click 'Generate QR Code'",
                "4. QR code is created automatically",
                "5. Download or print the QR code",
                "6. Use QR code for quick facility identification"
            ],
            "view_facilities": [
                "1. Click 'Facility Management'",
                "2. Select 'View Facilities' or 'Facility List'",
                "3. Use filters to narrow down results",
                "4. Click on any facility to see details",
                "5. View images, QR codes, and history"
            ],
            "edit_facility": [
                "1. Go to Facility List",
                "2. Click on the facility you want to edit",
                "3. Click 'Edit' or 'Update' button",
                "4. Modify the details",
                "5. Click 'Save Changes'",
                "Note: Only Area Managers can edit facilities"
            ]
        }
    },
    
    "quality_assessment": {
        "description": "Quality assessment and evaluation system",
        "features": [
            "Standard vs recent image comparison",
            "Technical activity logging",
            "Quality evaluation forms",
            "Assessment reports"
        ],
        "user_groups": ["EV", "AM"],
        "urls": {
            "assessment": "/assessment/",
            "evaluation": "/evaluation/",
            "reports": "/reports/"
        }
    },
    
    "technical_activities": {
        "description": "Technical activities tracking and management",
        "features": [
            "Log daily technical activities",
            "Upload before/after images",
            "Track activity locations",
            "Set risk levels and priorities",
            "Add remarks and comments",
            "Generate activity reports",
            "View activity history"
        ],
        "user_groups": ["EMP", "AM", "EV"],
        "urls": {
            "main": "/tech-activities/",
            "create": "/tech-activities/create/",
            "list": "/tech-activities/list/",
            "upload": "/tech-activities/upload/"
        },
        "how_to": {
            "log_activity": [
                "1. Go to 'Technical Activities' in the menu",
                "2. Click 'Create New Activity' or 'Log Activity'",
                "3. Fill in activity details:",
                "   - Activity name and description",
                "   - Facility location",
                "   - Risk level (operational, environmental, etc.)",
                "   - Priority level",
                "4. Upload images (before and after if applicable)",
                "5. Add any remarks or notes",
                "6. Click 'Submit' to save"
            ],
            "upload_images": [
                "1. Navigate to Technical Activities",
                "2. Select 'Upload Images' or find your activity",
                "3. Click 'Add Images' button",
                "4. Select images from your device",
                "5. Add captions or descriptions for each image",
                "6. Specify if it's a 'before' or 'after' image",
                "7. Click 'Upload'",
                "Note: Maximum file size is 50MB per image"
            ],
            "view_activities": [
                "1. Click 'Technical Activities'",
                "2. Select 'View All Activities' or 'Activity List'",
                "3. Use filters to find specific activities:",
                "   - By date range",
                "   - By risk level",
                "   - By location",
                "   - By user who created it",
                "4. Click on any activity to see full details"
            ],
            "edit_activity": [
                "1. Find the activity in your list",
                "2. Click on it to open details",
                "3. Click 'Edit' button",
                "4. Update information as needed",
                "5. Click 'Save Changes'",
                "Note: You can only edit your own activities (unless you're an Area Manager)"
            ]
        },
        "risk_levels": {
            "operational": "Activities affecting daily operations",
            "environmental": "Activities with environmental impact",
            "safety": "Safety-related activities requiring immediate attention",
            "maintenance": "Routine maintenance activities",
            "critical": "Critical issues requiring urgent action"
        }
    },
    
    "reports_and_statistics": {
        "description": "Generate reports and view statistics",
        "features": [
            "PDF report generation",
            "Facility reports",
            "Activity summary reports",
            "Quality assessment reports",
            "Regional statistics",
            "Export data to Excel/PDF",
            "Date range filtering",
            "Custom report generation"
        ],
        "user_groups": ["AM", "EV"],
        "how_to": {
            "generate_facility_report": [
                "1. Go to 'Reports' section",
                "2. Select 'Facility Reports'",
                "3. Choose the facility from dropdown",
                "4. Select date range if needed",
                "5. Click 'Generate PDF Report'",
                "6. Report will download automatically",
                "Report includes: Facility details, QR code, images, activity history"
            ],
            "generate_activity_report": [
                "1. Navigate to 'Reports'",
                "2. Select 'Activity Reports'",
                "3. Set filters:",
                "   - Date range",
                "   - Risk level",
                "   - Region",
                "   - User",
                "4. Click 'Generate Report'",
                "5. Download PDF or Excel version"
            ],
            "view_statistics": [
                "1. Go to Dashboard or 'Statistics' page",
                "2. View real-time statistics:",
                "   - Total facilities and QR coverage",
                "   - Activities this month/week",
                "   - Risk distribution",
                "   - Pending assessments",
                "3. Click on any stat for detailed breakdown",
                "4. Use 'Refresh' to update data"
            ],
            "export_data": [
                "1. Go to the section you want to export (Facilities, Activities, etc.)",
                "2. Apply any filters you need",
                "3. Click 'Export' button (usually top right)",
                "4. Choose format: Excel or PDF",
                "5. File will download to your device"
            ]
        }
    },
    
    "faq": {
        "dashboard_questions": {
            "q1": {
                "question": "What can I see on the dashboard?",
                "answer": "The dashboard shows your regional overview including total facilities, QR code coverage, recent technical activities, risk distribution, and quick access links. What you see depends on your role (AM/EMP/EV) and region (C2/Danao/Mindanao)."
            },
            "q2": {
                "question": "How do I navigate to different sections?",
                "answer": "Use the main navigation menu at the top. You'll see options for Dashboard, Facilities, Technical Activities, Quality Assessment, and Reports. Click any section to access its features."
            },
            "q3": {
                "question": "Why can't I see certain menu items?",
                "answer": "Menu items are role-based. Employees (EMP) see activity logging features. Evaluators (EV) see assessment features. Area Managers (AM) see everything. Contact your administrator if you need access to additional features."
            },
            "q4": {
                "question": "How do I check facility statistics?",
                "answer": "Go to the Dashboard or ask the chatbot 'Show me statistics' or 'How many facilities?' to get real-time data from your database."
            },
            "q5": {
                "question": "What are QR codes used for?",
                "answer": "QR codes uniquely identify each facility. They're used for quick facility lookup, mobile scanning, and linking physical locations to the system. Generate them in Facility Management section."
            }
        },
        "common_tasks": {
            "q1": {
                "question": "How do I add a new facility?",
                "answer": "Go to Facility Management → Create New Facility. Fill in the name, location, and region. Click Save. Then generate a QR code if needed."
            },
            "q2": {
                "question": "How do I log a technical activity?",
                "answer": "Navigate to Technical Activities → Create New Activity. Fill in details, select facility, set risk level, upload images, and submit. Images should show before/after if applicable."
            },
            "q3": {
                "question": "How do I upload images?",
                "answer": "In Technical Activities, click Upload Images. Select your activity, choose image files (max 50MB each), add descriptions, and upload. Supports JPG and PNG formats."
            },
            "q4": {
                "question": "How do I generate a report?",
                "answer": "Go to Reports section. Choose report type (Facility/Activity/Assessment). Select date range and filters. Click Generate PDF. Report downloads automatically."
            },
            "q5": {
                "question": "How do I search for a facility?",
                "answer": "Go to Facility List and use the search box at the top. You can search by name, location, or ID. You can also ask the chatbot 'Search for facility [name]'."
            },
            "q6": {
                "question": "What if I make a mistake in an activity?",
                "answer": "Find your activity in the list, click it, then click Edit. Make your changes and save. Note: You can only edit your own activities unless you're an Area Manager."
            },
            "q7": {
                "question": "How do I see activities by date?",
                "answer": "In Technical Activities list, use the date filter at the top. Select start and end dates, then click Filter or Apply. Results will show activities within that range."
            },
            "q8": {
                "question": "How do I download a QR code?",
                "answer": "Go to Facility Management, find your facility, click on it, then click Download QR Code. It will save as an image file you can print."
            }
        },
        "troubleshooting": {
            "q1": {
                "question": "Images won't upload",
                "answer": "Check: 1) File size under 50MB, 2) Format is JPG or PNG, 3) Internet connection is stable. Try reducing image size if needed."
            },
            "q2": {
                "question": "Can't see my facilities",
                "answer": "Check: 1) You're in the correct region view, 2) No active filters hiding results, 3) You have permission to view facilities. Try refreshing the page."
            },
            "q3": {
                "question": "Report generation fails",
                "answer": "Check: 1) You have permission to generate reports (AM/EV only), 2) Selected facilities/activities exist, 3) Date range is valid. Try a smaller date range."
            },
            "q4": {
                "question": "Statistics not showing",
                "answer": "Try refreshing the page. Statistics load from the database and may take a moment. You can also ask the chatbot 'Show me statistics' for current data."
            },
            "q5": {
                "question": "Can't edit a facility",
                "answer": "Only Area Managers (AM) can edit facilities. If you're an AM and still can't edit, check that you're viewing your assigned region."
            }
        }
    },
    
    "user_groups": {
        "AM": {
            "name": "Area Manager",
            "permissions": [
                "Manage facilities",
                "Oversee quality assessments",
                "Generate reports",
                "Access all regional data"
            ],
            "regions": ["C2", "Danao", "Mindanao"]
        },
        "EMP": {
            "name": "Employee",
            "permissions": [
                "Upload images",
                "Log technical activities",
                "View assigned facilities"
            ],
            "regions": ["C2", "Danao", "Mindanao"]
        },
        "EV": {
            "name": "Evaluator",
            "permissions": [
                "Conduct quality assessments",
                "Evaluate technical activities",
                "Generate assessment reports"
            ],
            "regions": ["C2", "Danao", "Mindanao"]
        }
    },
    
    "regions": {
        "C2": {
            "name": "C2 Region",
            "description": "Main operational region",
            "user_groups": ["AM", "EMP", "EV"]
        },
        "Danao": {
            "name": "Danao Region",
            "description": "Secondary operational region",
            "user_groups": ["AM_D", "EMP_D", "EV_D"]
        },
        "Mindanao": {
            "name": "Mindanao Region",
            "description": "Third operational region",
            "user_groups": ["AM_M", "EMP_M", "EV_M"]
        }
    },
    
    "common_tasks": {
        "qr_code_generation": {
            "steps": [
                "1. Navigate to Facility Management",
                "2. Select 'Generate QR Code'",
                "3. Enter facility details",
                "4. Download generated QR code"
            ],
            "url": "/facility-management/qr-generate/"
        },
        "image_upload": {
            "steps": [
                "1. Go to Technical Activities",
                "2. Select 'Upload Images'",
                "3. Choose facility location",
                "4. Upload images with descriptions"
            ],
            "url": "/activities/upload/"
        },
        "quality_assessment": {
            "steps": [
                "1. Access Quality Assessment section",
                "2. Compare standard vs recent images",
                "3. Complete evaluation form",
                "4. Submit assessment"
            ],
            "url": "/assessment/"
        },
        "report_generation": {
            "steps": [
                "1. Go to Reports section",
                "2. Select report type",
                "3. Choose date range and filters",
                "4. Generate and download PDF"
            ],
            "url": "/reports/"
        }
    },
    
    "troubleshooting": {
        "login_issues": {
            "common_causes": [
                "Incorrect username/password",
                "Account locked",
                "User group permissions"
            ],
            "solutions": [
                "Contact system administrator",
                "Check user group assignment",
                "Verify account status"
            ]
        },
        "upload_issues": {
            "common_causes": [
                "File size too large",
                "Unsupported file format",
                "Network connectivity"
            ],
            "solutions": [
                "Reduce file size (max 50MB)",
                "Use supported formats (JPG, PNG)",
                "Check internet connection"
            ]
        },
        "permission_denied": {
            "common_causes": [
                "Insufficient user group permissions",
                "Regional access restrictions",
                "Feature not available for role"
            ],
            "solutions": [
                "Contact administrator for permission",
                "Verify regional access rights",
                "Check user group assignment"
            ]
        }
    }
}

def get_contextual_response(user_message: str, user_groups: list = None, region: str = None, user_context: dict = None) -> str:
    """
    Generate contextual responses based on user's role and region with database integration
    """
    try:
        user_message_lower = user_message.lower()
        user_id = user_context.get('user_id') if user_context else None
        
        # Database query patterns
        if any(word in user_message_lower for word in ['show', 'list', 'count', 'how many', 'statistics', 'stats']):
            return _get_database_response(user_message_lower, user_groups, region, user_id)
        
        elif any(word in user_message_lower for word in ['search', 'find', 'look for']):
            return _get_search_response(user_message_lower, user_groups, region, user_id)
        
        elif any(word in user_message_lower for word in ['my', 'my activities', 'my uploads']):
            return _get_user_specific_response(user_message_lower, user_groups, region, user_id)
        
        # Skip greetings and thanks - let AI handle these naturally
        # Conversational messages should be handled by the AI service for natural responses
        
        # Dashboard queries
        elif any(word in user_message_lower for word in ['dashboard', 'main page', 'home page', 'overview']):
            return _get_dashboard_response(user_message_lower, user_groups, region)
        
        # FAQ / Common questions
        elif any(phrase in user_message_lower for phrase in ['how do i', 'how can i', 'how to', 'can i', 'where do i']):
            return _get_faq_response(user_message_lower, user_groups)
        
        # Navigation help
        elif any(word in user_message_lower for word in ['navigate', 'menu', 'where is', 'find page']):
            return _get_navigation_response(user_message_lower, user_groups)
        
        # Feature queries
        elif any(word in user_message_lower for word in ['qr', 'qr code', 'facility code']):
            return _get_facility_management_response(user_message_lower, user_groups)
        
        elif any(word in user_message_lower for word in ['assessment', 'quality', 'evaluation']):
            return _get_quality_assessment_response(user_message_lower, user_groups)
        
        elif any(word in user_message_lower for word in ['activity', 'technical', 'upload']):
            return _get_technical_activities_response(user_message_lower, user_groups)
        
        elif any(word in user_message_lower for word in ['report', 'pdf', 'download']):
            return _get_report_response(user_message_lower, user_groups)
        
        elif any(word in user_message_lower for word in ['permission', 'access', 'denied']):
            return _get_permission_response(user_message_lower, user_groups, region)
        
        elif any(word in user_message_lower for word in ['help', 'how to', 'tutorial']):
            return _get_help_response(user_message_lower, user_groups)
        
        else:
            return _get_general_response(user_message_lower, user_groups, region)
    
    except Exception as e:
        print(f"Knowledge base error: {str(e)}")
        return _get_general_response(user_message.lower() if user_message else "", user_groups or [], region or "C2")

def _get_facility_management_response(message: str, user_groups: list) -> str:
    """Generate facility management specific response"""
    if not user_groups:
        return "Facility management features include QR code generation, facility tracking, and location management. Please log in to access these features."
    
    # Check if user has facility management permissions
    facility_groups = ["AM", "EMP", "EV", "AM_D", "EMP_D", "EV_D", "AM_M", "EMP_M", "EV_M"]
    has_access = any(group in facility_groups for group in user_groups)
    
    if has_access:
        return """For facility management:
        
• **QR Code Generation**: Navigate to Facility Management → Generate QR Code
• **Facility Tracking**: View and track facility status in the dashboard
• **Image Upload**: Upload facility images for documentation
• **Location Management**: Manage facility locations and details

Your user group has access to facility management features. Would you like specific help with any of these features?"""
    else:
        return "Facility management features require appropriate user permissions. Please contact your administrator if you need access."

def _get_quality_assessment_response(message: str, user_groups: list) -> str:
    """Generate quality assessment specific response"""
    assessment_groups = ["EV", "AM", "EV_D", "AM_D", "EV_M", "AM_M"]
    has_access = any(group in assessment_groups for group in user_groups) if user_groups else False
    
    if has_access:
        return """For quality assessment:
        
• **Image Comparison**: Compare standard vs recent facility images
• **Evaluation Forms**: Complete quality evaluation assessments
• **Assessment Reports**: Generate quality assessment reports
• **Technical Review**: Review and approve technical activities

Access the Quality Assessment section from your dashboard. Would you like help with a specific assessment task?"""
    else:
        return "Quality assessment features are available to Evaluators and Area Managers. Contact your administrator if you need access to these features."

def _get_technical_activities_response(message: str, user_groups: list) -> str:
    """Generate technical activities specific response"""
    activity_groups = ["EMP", "AM", "EV", "EMP_D", "AM_D", "EV_D", "EMP_M", "AM_M", "EV_M"]
    has_access = any(group in activity_groups for group in user_groups) if user_groups else False
    
    if has_access:
        return """For technical activities:
        
• **Activity Logging**: Log technical activities with timestamps
• **Image Upload**: Upload images for activity documentation
• **Location Tracking**: Record activity locations
• **Activity Reports**: Generate activity reports

Go to Technical Activities section to start logging activities. Need help with a specific activity type?"""
    else:
        return "Technical activities features require appropriate user permissions. Please contact your administrator for access."

def _get_report_response(message: str, user_groups: list) -> str:
    """Generate report specific response"""
    report_groups = ["AM", "EV", "AM_D", "EV_D", "AM_M", "EV_M"]
    has_access = any(group in report_groups for group in user_groups) if user_groups else False
    
    if has_access:
        return """For report generation:
        
• **Facility Reports**: Generate facility assessment reports
• **Activity Reports**: Create technical activity summaries
• **Quality Reports**: Generate quality evaluation reports
• **Regional Reports**: Create region-specific reports

Access the Reports section from your dashboard. What type of report do you need?"""
    else:
        return "Report generation is available to Area Managers and Evaluators. Contact your administrator if you need report access."

def _get_permission_response(message: str, user_groups: list, region: str) -> str:
    """Generate permission/access specific response"""
    if not user_groups:
        return "Access issues may be related to user permissions or regional restrictions. Please contact your system administrator for assistance."
    
    return f"""Based on your current permissions:
        
• **Your Groups**: {', '.join(user_groups)}
• **Region**: {region or 'Not specified'}
        
If you're experiencing access issues:
1. Verify your user group permissions
2. Check regional access restrictions
3. Contact your system administrator
4. Ensure you're accessing the correct regional section

What specific feature are you trying to access?"""

def _get_help_response(message: str, user_groups: list) -> str:
    """Generate general help response"""
    if not user_groups:
        return """Welcome to the OMS Assistant! I can help you with:
        
• Facility Management (QR codes, tracking)
• Quality Assessment (evaluations, reports)
• Technical Activities (logging, uploads)
• Report Generation (PDFs, summaries)
• User Permissions (access issues)
        
Please log in to get personalized help based on your user role."""
    
    return f"""I'm here to help with your OMS operations! Based on your user groups ({', '.join(user_groups)}), you have access to:
        
• **Facility Management**: QR codes, facility tracking
• **Technical Activities**: Activity logging, image uploads
• **Quality Assessment**: Evaluations, assessments
• **Reports**: Generate various operational reports
        
What specific task would you like help with?"""

def _get_general_response(message: str, user_groups: list, region: str) -> str:
    """Generate general contextual response"""
    return """I'm your OMS Assistant, trained to help with Operations Management System tasks.

I can assist with:
• Facility management and QR code generation
• Quality assessment and evaluation processes  
• Technical activity logging and documentation
• Report generation and data analysis
• User permissions and access issues
• Regional operations (C2, Danao, Mindanao)
• **Live data queries** - Ask me to show statistics, search facilities, or list activities!

How can I help you with your OMS operations today?"""

def _get_database_response(message: str, user_groups: list, region: str, user_id: int) -> str:
    """Generate database-driven responses for data queries"""
    try:
        if any(word in message for word in ['facility', 'facilities']):
            data = db_service.get_facilities_summary(region, user_groups)
            if 'error' in data:
                return f"Sorry, I couldn't retrieve facility data: {data['error']}"
            
            response = f"""**Facility Summary for {region} Region**

**Overview:**
   • Total Facilities: **{data['total_facilities']}**
   • With QR Codes: **{data['facilities_with_qr']}**
   • Without QR Codes: **{data['facilities_without_qr']}**
   • Added This Month: **{data['recent_facilities']}**

**Recent Facilities:**
"""
            for facility in data['facility_list'][:5]:
                qr_status = "[HAS QR]" if facility['has_qr'] else "[NO QR]"
                response += f"   • {qr_status} **{facility['name']}**\n"
                response += f"     Created: {facility['created']}\n\n"
            
            return response
        
        elif any(word in message for word in ['activity', 'activities', 'technical']):
            data = db_service.get_tech_activities_summary(region, user_groups, user_id)
            if 'error' in data:
                return f"Sorry, I couldn't retrieve activity data: {data['error']}"
            
            response = f"""**Technical Activities Summary for {region} Region**

**Overview:**
   • Total Activities: **{data['total_activities']}**
   • This Month: **{data['activities_this_month']}**
   • This Week: **{data['activities_this_week']}**
   • Pending Remarks: **{data['pending_remarks']}**

**Risk Distribution:**
"""
            for risk, count in data['risk_distribution'].items():
                response += f"   • {risk}: **{count}**\n"
            
            response += "\n**Recent Activities:**\n"
            for activity in data['recent_activities'][:5]:
                risk_indicator = "[HIGH RISK]" if activity['risk'] in ['operational', 'environmental'] else "[MEDIUM RISK]"
                response += f"   • {risk_indicator} **{activity['name']}**\n"
                response += f"     Location: {activity['location']}\n"
                response += f"     Date: {activity['created']}\n"
                response += f"     By: {activity['uploaded_by']}\n\n"
            
            return response
        
        elif any(word in message for word in ['statistics', 'stats', 'overview']):
            data = db_service.get_statistics(region, user_groups)
            if 'error' in data:
                return f"Sorry, I couldn't retrieve statistics: {data['error']}"
            
            return f"""**OMS Statistics for {region} Region**

**Facilities:**
   • Total: **{data['facilities']['total']}**
   • With QR Codes: **{data['facilities']['with_qr_codes']}** ({data['facilities']['qr_coverage_percentage']}% coverage)
   • Without QR Codes: **{data['facilities']['without_qr_codes']}**

**Activities:**
   • Total: **{data['activities']['total']}**
   • This Month: **{data['activities']['this_month']}**
   • High Risk: **{data['activities']['high_risk']}**
   • Critical Priority: **{data['activities']['critical_priority']}**

---
*Generated: {data['generated_at']}*"""
        
        else:
            return "I can show you data about facilities, activities, or overall statistics. What would you like to see?"
    
    except Exception as e:
        return f"Sorry, I encountered an error retrieving data: {str(e)}"

def _get_search_response(message: str, user_groups: list, region: str, user_id: int) -> str:
    """Generate search-based responses"""
    try:
        # Extract search terms from common patterns
        search_terms = []
        
        # Look for patterns like "search for X" or "find X"
        if 'search for' in message:
            search_terms = message.split('search for')[1].strip()
        elif 'find' in message:
            search_terms = message.split('find')[1].strip()
        elif 'look for' in message:
            search_terms = message.split('look for')[1].strip()
        
        if not search_terms:
            return "What would you like me to search for? Try 'search for [facility name]' or 'find [activity name]'"
        
        # Determine if searching facilities or activities
        if any(word in message for word in ['facility', 'facilities']):
            data = db_service.search_facilities(search_terms, region, user_groups)
            if 'error' in data:
                return f"Search error: {data['error']}"
            
            if data['total_found'] == 0:
                return f"No facilities found matching '{search_terms}' in {region} region."
            
            response = f"**Found {data['total_found']} facilities matching '{search_terms}':**\n\n"
            for facility in data['facilities']:
                qr_status = "[HAS QR]" if facility['has_qr'] else "[NO QR]"
                response += f"• {qr_status} **{facility['name']}**\n"
                response += f"  ID: {facility['id']}\n"
                response += f"  Created: {facility['created']}\n\n"
            
            return response
        
        else:  # Default to activity search
            data = db_service.search_activities(search_terms, region, user_id)
            if 'error' in data:
                return f"Search error: {data['error']}"
            
            if data['total_found'] == 0:
                return f"No activities found matching '{search_terms}' in {region} region."
            
            response = f"**Found {data['total_found']} activities matching '{search_terms}':**\n\n"
            for activity in data['activities']:
                risk_indicator = "[HIGH RISK]" if activity['risk'] in ['operational', 'environmental'] else "[MEDIUM RISK]"
                response += f"• {risk_indicator} **{activity['name']}**\n"
                response += f"  Location: {activity['location']}\n"
                response += f"  Uploaded by: {activity['uploaded_by']}\n"
                response += f"  Risk: {activity['risk']} | Priority: {activity['priority']}\n"
                response += f"  Created: {activity['created']}\n"
                response += f"  Images: {activity['images_count']}\n\n"
            
            return response
    
    except Exception as e:
        return f"Sorry, I encountered an error during search: {str(e)}"

def _get_user_specific_response(message: str, user_groups: list, region: str, user_id: int) -> str:
    """Generate user-specific data responses"""
    if not user_id:
        return "I need your user information to show your specific data. Please make sure you're logged in."
    
    try:
        data = db_service.get_user_activities(user_id, region)
        if 'error' in data:
            return f"Sorry, I couldn't retrieve your data: {data['error']}"
        
        response = f"""**Your Activities in {region} Region**

**Overview:**
   • Total Activities: **{data['user_total_activities']}**
   • This Month: **{data['user_activities_this_month']}**

**Your Recent Activities:**
"""
        for activity in data['user_recent_activities']:
            risk_indicator = "[HIGH RISK]" if activity['risk'] in ['operational', 'environmental'] else "[MEDIUM RISK]"
            response += f"• {risk_indicator} **{activity['name']}**\n"
            response += f"  Location: {activity['location']}\n"
            response += f"  Risk: {activity['risk']} | Priority: {activity['priority']}\n"
            response += f"  Created: {activity['created']}\n"
            response += f"  Images: {activity['images_count']}\n\n"
        
        return response
    
    except Exception as e:
        return f"Sorry, I encountered an error retrieving your data: {str(e)}"

def _get_greeting_response(user_groups: list, region: str) -> str:
    """Generate personalized greeting response"""
    if not user_groups:
        return """Hello! I'm your OMS Assistant. I can help you with operations management tasks.

**Available Features:**
• Live data queries - statistics, search, analytics
• Facility management - QR codes, tracking, locations
• Technical activities - logging, uploads, documentation
• Quality assessment - evaluations, reports
• User support - permissions, troubleshooting

**Try asking me:**
- "Show me facility statistics"
- "How many activities this month?"
- "Search for facility [name]"

Please log in to access your personalized data and regional information."""

    return f"""Hello! I'm your OMS Assistant for the {region} region.

I can help you with:
• **Live Data Queries** - Ask me to show statistics, search facilities, or list activities
• **Facility Management** - QR codes, facility tracking, location management  
• **Technical Activities** - Activity logging, image uploads, documentation
• **Quality Assessment** - Evaluations, assessments, reports
• **Personal Data** - Your activities, uploads, and history

**Quick Actions - Try asking:**
• "Show me facility statistics"
• "How many activities this month?"
• "Search for facility [name]"
• "Show my activities"

Based on your role ({', '.join(user_groups)}), you have access to comprehensive OMS features.

How can I help you today?"""

def _get_thanks_response() -> str:
    """Generate thank you response"""
    return """You're welcome! I'm here to help with your OMS operations.

**Remember, I can:**
• Show live data from your database
• Search facilities and activities
• Provide personalized insights
• Help with troubleshooting
• Guide you through OMS processes

Feel free to ask me anything about your operations management system!"""

def _get_dashboard_response(message: str, user_groups: list, region: str) -> str:
    """Generate dashboard-specific response"""
    kb_dashboard = OMS_KNOWLEDGE_BASE.get('dashboard', {})
    
    if 'what' in message and 'see' in message:
        # "What can I see on dashboard?"
        return f"""**Dashboard Overview for {region} Region**

Your dashboard shows:

📊 **Statistics:**
• Total facilities and QR code coverage
• Recent technical activities (this week/month)
• Risk distribution (operational, environmental, safety)
• Pending assessments and evaluations

📈 **Quick Access:**
• Create new facility
• Log technical activity
• Generate reports
• View facility list

🎯 **Based on Your Role ({', '.join(user_groups)}):**
{'• Full management access - you can see all regional data and perform all actions' if any('AM' in g for g in user_groups) else ''}
{'• Activity logging and image upload access' if any('EMP' in g for g in user_groups) else ''}
{'• Quality assessment and evaluation access' if any('EV' in g for g in user_groups) else ''}

**Try asking:**
• "Show me statistics"
• "How many facilities?"
• "Show my activities"
"""
    
    elif 'navigate' in message or 'menu' in message:
        return """**Dashboard Navigation**

Use the main menu at the top to access:

🏢 **Facility Management**
   • Create/View facilities
   • Generate QR codes
   • Manage locations

⚙️ **Technical Activities**
   • Log activities
   • Upload images
   • View activity history

✅ **Quality Assessment** (EV/AM only)
   • Conduct evaluations
   • Compare images
   • Generate assessment reports

📄 **Reports** (AM/EV only)
   • Facility reports
   • Activity summaries
   • Export data

What would you like to access?"""
    
    else:
        return f"""**Dashboard Help for {region} Region**

The dashboard is your control center for OMS operations.

**Main Features:**
• View real-time statistics and summaries
• Quick access to all major functions
• Recent activity overview
• Role-based menu items

**Your Permissions ({', '.join(user_groups)}):**
You can access features based on your role. The dashboard shows only what's available to you.

**Quick Tips:**
• Statistics update automatically
• Click any number for detailed view
• Use search to find specific items
• Refresh page to update data

What specific dashboard feature would you like to know about?"""

def _get_faq_response(message: str, user_groups: list) -> str:
    """Generate FAQ-based response"""
    faq = OMS_KNOWLEDGE_BASE.get('faq', {})
    
    # Check for specific common questions
    if 'add' in message and 'facility' in message:
        return """**How to Add a New Facility**

1. Click **'Facility Management'** in the main menu
2. Select **'Create New Facility'**
3. Fill in the required information:
   • Facility Name
   • Location/Address
   • Region (C2/Danao/Mindanao)
   • Description (optional)
4. Click **'Save'**
5. (Optional) Generate QR code for the facility

**Need Help?**
• Only Area Managers can create facilities
• All fields marked with * are required
• You can add images after creating the facility

Try it now from the Facility Management section!"""
    
    elif 'log' in message and 'activity' in message:
        return """**How to Log a Technical Activity**

1. Go to **'Technical Activities'** in the menu
2. Click **'Create New Activity'** or **'Log Activity'**
3. Fill in the activity details:
   • Activity name and description
   • Select facility/location
   • Choose risk level (operational, environmental, safety, etc.)
   • Set priority level
4. Upload images:
   • Before images (initial state)
   • After images (completed work)
   • Max 50MB per image
5. Add any remarks or comments
6. Click **'Submit'** to save

**Pro Tips:**
• Upload clear, well-lit images
• Include date and time in description
• Select accurate risk level for tracking
• You can edit your activities later

Start logging from Technical Activities section!"""
    
    elif 'upload' in message and 'image' in message:
        return """**How to Upload Images**

**Method 1 - With New Activity:**
1. Create a new technical activity
2. Click 'Add Images' during creation
3. Select files from your device
4. Add descriptions for each image
5. Submit activity

**Method 2 - To Existing Activity:**
1. Go to Technical Activities list
2. Find and click on your activity
3. Click 'Add Images' or 'Upload'
4. Select images (JPG or PNG)
5. Add captions and click Upload

**Image Requirements:**
✓ Max size: 50MB per image
✓ Formats: JPG, PNG
✓ Recommended: Clear, well-lit photos
✓ Label: Before/After/During

**Troubleshooting:**
• File too large? Resize or compress it
• Upload failing? Check internet connection
• Can't add images? Check permissions"""
    
    elif 'generate' in message and 'report' in message:
        return """**How to Generate a Report**

1. Click **'Reports'** in the main menu
2. Select report type:
   • **Facility Report** - Details of specific facility
   • **Activity Report** - Technical activities summary
   • **Assessment Report** - Quality evaluations
3. Set your filters:
   • Select facility/activity
   • Choose date range
   • Pick region (if applicable)
4. Click **'Generate PDF Report'**
5. Report downloads automatically

**Report Features:**
• Professional PDF format
• Includes images and QR codes
• Date-stamped and signed
• Ready to print or share

**Note:** Only Area Managers and Evaluators can generate reports.

Access Reports section now!"""
    
    elif 'search' in message and 'facility' in message:
        return """**How to Search for a Facility**

**Method 1 - Using Search Box:**
1. Go to Facility Management → Facility List
2. Use the search box at the top
3. Type facility name, location, or ID
4. Results appear instantly

**Method 2 - Ask the Chatbot:**
Just ask me: "Search for facility [name]"
I'll query the database and show results!

**Method 3 - Use Filters:**
1. Go to Facility List
2. Click 'Filters' button
3. Select region, QR status, date range
4. Click 'Apply'

**Search Tips:**
• Use partial names (e.g., "Station" finds "Gas Station 1")
• Filter by region for faster results
• Click facility for full details

Try searching now!"""
    
    elif 'qr' in message or 'qr code' in message:
        return """**QR Code Features**

**What are QR Codes used for?**
• Unique identification for each facility
• Quick facility lookup via mobile scan
• Linking physical locations to digital records
• Fast access to facility information

**How to Generate QR Code:**
1. Go to Facility Management
2. Find your facility
3. Click 'Generate QR Code'
4. QR code creates automatically
5. Download or print it

**How to Download/Print:**
1. Open facility details
2. Click 'Download QR Code'
3. Saves as image file
4. Print and attach to facility location

**Scanning QR Codes:**
• Use any QR scanner app
• Scans directly to facility details
• Works on any mobile device

**Pro Tip:** Generate QR codes for all facilities to enable quick mobile access!"""
    
    else:
        # General FAQ response
        return """**Frequently Asked Questions**

**Common Tasks:**
• "How do I add a new facility?"
• "How do I log a technical activity?"
• "How do I upload images?"
• "How do I generate a report?"
• "How do I search for a facility?"
• "What are QR codes used for?"
• "How do I download a QR code?"

**Navigation:**
• "Where is the dashboard?"
• "How do I navigate the menu?"
• "Why can't I see certain features?"

**Troubleshooting:**
• "Images won't upload"
• "Can't see my facilities"
• "Report generation fails"

**Ask me any specific question, like:**
"How do I add a new facility?"
"Show me how to upload images"
"Help me generate a report"

What do you need help with?"""

def _get_navigation_response(message: str, user_groups: list) -> str:
    """Generate navigation help response"""
    return """**OMS Navigation Guide**

**Main Menu Sections:**

🏠 **Dashboard** (Home Page)
   • Overview and statistics
   • Recent activities
   • Quick access links

🏢 **Facility Management**
   • Create New Facility
   • View Facility List
   • Generate QR Codes
   • Manage Locations

⚙️ **Technical Activities**
   • Log New Activity
   • View Activity List
   • Upload Images
   • Activity History

✅ **Quality Assessment** (Evaluators & Managers)
   • Conduct Evaluations
   • Image Comparison
   • Assessment Forms
   • View Results

📄 **Reports** (Managers & Evaluators)
   • Generate Facility Reports
   • Activity Summaries
   • Assessment Reports
   • Export Data

**Your Access Level:**
Based on your role ({', '.join(user_groups)}), you can see:
{
    '• All sections - Full access' if any('AM' in g for g in user_groups) else
    '• Facilities and Technical Activities sections' if any('EMP' in g for g in user_groups) else
    '• Facilities, Activities, Assessments, and Reports' if any('EV' in g for g in user_groups) else
    '• Limited sections based on permissions'
}

**Navigation Tips:**
• Use the top menu to switch between sections
• Breadcrumb links show your current location
• 'Home' button returns to dashboard
• Back button in your browser works

Where would you like to go?"""
