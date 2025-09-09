# OMS - Operations Management System

A comprehensive Django-based Operations Management System designed for facility management and quality assessment across multiple Strategic Business Units (SBUs). The system supports three main regions: C2, Danao, and Mindanao, each with their own user groups and facilities.

## 🚀 Features

### Core Functionality
- **Multi-SBU Support**: Separate management for C2, Danao, and Mindanao regions
- **Role-Based Access Control**: Different user groups (AM, EMP, EV) with specific permissions
- **Facility Management**: QR code generation and facility tracking
- **Image Assessment System**: Standard vs. recent image comparison
- **Technical Activities Tracking**: Activity logging with image uploads
- **Rich Text Editor**: CKEditor integration for detailed remarks
- **PDF Report Generation**: Automated report generation with company branding

### User Groups
- **AM (Area Manager)**: Management oversight and assessment capabilities
- **EMP (Employee)**: Image upload and basic operations
- **EV (Evaluator)**: Quality assessment and evaluation functions

### Regional Support
- **C2**: Main operational region
- **Danao**: Secondary operational region with separate user groups (AM_D, EMP_D, EV_D)
- **Mindanao**: Third operational region with separate user groups (AM_M, EMP_M, EV_M)

## 🛠️ Technology Stack

- **Backend**: Django 5.0.6
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Image Processing**: Pillow
- **QR Code Generation**: django-qrcode
- **Rich Text Editor**: django-ckeditor
- **PDF Generation**: ReportLab
- **Static Files**: WhiteNoise
- **Environment Management**: django-environ

## 📋 Prerequisites

- Python 3.8+
- MySQL Database
- Virtual Environment (recommended)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd oms
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root with the following variables:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_NAME=oms_database
   DATABASE_USER=your-db-user
   DATABASE_PASSWORD=your-db-password
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   IMAGE_ENV=development
   BASE_URL=http://localhost:8000
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create User Groups**
   ```bash
   python manage.py runscript create_groups_script
   ```

7. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
oms/
├── core/                   # Core functionality and shared models
├── c2/                     # C2 region management
├── danao/                  # Danao region management
├── mindanao/               # Mindanao region management
├── members/                # User authentication
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploaded files
├── Documentation/          # Project documentation
└── requirements.txt        # Python dependencies
```

## 🔐 User Management

### Default Test Accounts

**C2 Region:**
- Username: `doejohn` | Password: `$Everyday23` | Group: AM
- Username: `doejason` | Password: `$Everyday23` | Group: EMP
- Username: `doejane` | Password: `$Everyday23` | Group: EV

**Danao Region:**
- Username: `cruzxia` | Password: `$Everyday23` | Group: EV_D
- Username: `cruzaya` | Password: `$Everyday23` | Group: AM_D
- Username: `cruzthea` | Password: `$Everyday23` | Group: EMP_D

## 🎯 Key Features Explained

### QR Code System
- Each facility generates a unique QR code
- QR codes redirect to specific upload pages
- Dynamic URL generation based on environment settings

### Image Assessment
- **Standard Images**: Reference images for each facility
- **Recent Images**: Current condition images for comparison
- **Status Tracking**: Pass/Failed/Pending status with evaluator comments

### Technical Activities
- Activity logging with location tracking
- Image uploads for documentation
- Rich text remarks and comments
- Time-stamped entries

### Dashboard Features
- Real-time facility status updates
- Color-coded status indicators
- Recent activity tracking
- Assessment reports

## 🔧 Configuration

### Environment Variables
- `IMAGE_ENV`: Controls image storage path (development/production)
- `BASE_URL`: Base URL for QR code generation
- `DEBUG`: Django debug mode
- Database connection settings

### Media Files
- Development: `media/` directory
- Production: Configured server path
- Organized by region and type (standard_images, recent_images, technical_images, qrcodes)

## 📊 Database Models

### Core Models
- `SBU`: Strategic Business Unit management
- `StandardImage`: Base model for standard images
- `RecentImage`: Base model for recent images

### Regional Models
Each region (C2, Danao, Mindanao) has:
- `[Region]User`: User management with position tracking
- `[Region]Facility`: Facility management with QR codes
- `[Region]Standard`: Standard image management
- `[Region]RecentImage`: Recent image assessment
- `[Region]TechActivities`: Technical activity tracking
- `[Region]TechActivityImage`: Activity image attachments

## 🚀 Deployment

### Production Setup
1. Update `IMAGE_ENV` to "production"
2. Configure production database
3. Set up static file serving
4. Configure media file handling
5. Update `BASE_URL` to production domain
6. Set `DEBUG=False`

### Static Files
```bash
python manage.py collectstatic
```

## 📝 Usage

1. **Login**: Use provided test accounts or create new users
2. **Facility Management**: Create and manage facilities with QR codes
3. **Image Upload**: Upload standard and recent images for assessment
4. **Assessment**: Evaluate images and provide feedback
5. **Reports**: Generate PDF reports for failed assessments
6. **Technical Activities**: Log and track technical activities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software developed for internal use.

## 🆘 Support

For technical support or questions, please contact the development team.

## 📅 Recent Updates

- QR code system implementation
- Multi-region support
- Role-based access control
- PDF report generation
- Dashboard improvements
- Image assessment workflow

---

**Note**: This system is designed for internal operations management and requires proper authentication and authorization for access.
