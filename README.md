# AI Document Generator

An AI-powered platform for creating professional business documents (Word .docx and PowerPoint .pptx) with intelligent content generation and refinement capabilities.

## Features

- **AI-Assisted Content Generation**: Create structured documents using OpenAI's language models
- **Document Types**: Support for Microsoft Word documents and PowerPoint presentations
- **Template Generation**: AI-suggested document structures based on your topic
- **Content Refinement**: Iteratively improve content with AI-powered refinement prompts
- **Professional Styling**: Automatically styled documents with themes and proper formatting
- **Image Integration**: Relevant images automatically sourced and embedded
- **User Management**: Secure authentication and project management
- **Export Ready**: Download polished .docx and .pptx files

## Tech Stack

### Frontend
- **Next.js 16** with App Router
- **React 19** with TypeScript
- **Tailwind CSS 4** for styling
- **Lucide React** for icons

### Backend
- **FastAPI** with Python 3.10+
- **SQLAlchemy** ORM with PostgreSQL
- **OpenAI API** for content generation
- **python-docx** and **python-pptx** for document export
- **JWT** authentication with secure password hashing

### Database
- **PostgreSQL** for persistent storage

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL database
- OpenAI API key
- Google Chrome browser (for image search functionality)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The image service uses Selenium with Chrome WebDriver for reliable image search and download. See `backend/CHROME_SETUP.md` for detailed installation instructions. The ChromeDriver will be automatically downloaded and managed by webdriver-manager when first used.

4. Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql://username:password@host:port/database
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_jwt_secret_key
```

5. Test Chrome WebDriver setup (optional):
```bash
python test_chrome.py
```

6. Start the backend server:
```bash
python start.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

### Creating Your First Document

1. **Register/Login**: Create an account or sign in
2. **New Project**: Click "Create New Project" on the dashboard
3. **Configure**: Choose document type (Word/PowerPoint) and enter your topic
4. **Structure**: Define sections/slides manually or use AI template generation
5. **Generate**: Let AI create initial content for all sections/slides
6. **Refine**: Use refinement prompts to improve specific sections
7. **Export**: Download your polished document

### Document Types

**Word Documents**
- Define section headers and structure
- AI generates comprehensive content for each section
- Professional styling with proper headings and formatting
- Relevant images embedded inline

**PowerPoint Presentations**
- Specify slide titles and count
- AI creates engaging slide content
- Professional themes and layouts
- Strategic image placement (background/foreground)

### AI Features

**Template Generation**
- Input your topic and get AI-suggested document structure
- Customizable section headers or slide titles
- Smart content organization

**Content Refinement**
- Provide specific improvement prompts
- Iterative content enhancement
- Maintains refinement history

**Image Integration**
- Automatic image sourcing from public APIs
- Content-aware image selection
- Optimized placement and sizing

## API Documentation

When running in development mode, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/projects` - List user projects
- `POST /api/projects` - Create new project
- `POST /api/projects/{id}/generate` - Generate content
- `POST /api/sections/{id}/refine` - Refine section content
- `GET /api/projects/{id}/export` - Export document

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── models/             # SQLAlchemy database models
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic services
│   ├── schemas/            # Pydantic data models
│   └── dependencies/       # Shared dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── contexts/          # React contexts
│   ├── lib/              # API clients and utilities
│   └── types/            # TypeScript type definitions
└──
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations
The application automatically creates database tables on startup. For production deployments, consider using Alembic for proper migration management.

### Environment Configuration
- Development: Uses local database and OpenAI API
- Production: Requires proper environment variables and security configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the project specifications in `.kiro/specs/`
- Open an issue on the repository