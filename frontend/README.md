# Workflow Management System (WMS) - Frontend

A modern React 19 + TypeScript web application for managing workflow projects, users, clients, and stages with role-based access control.

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

   The app opens at `http://localhost:5173`

3. **Build for production**
   ```bash
   npm run build
   ```

   Output: `dist/` directory

## Features

### 🔐 Authentication & Authorization

- **Login System** - Secure authentication with JWT tokens
- **Forgot Password** - Password recovery flow
- **Role-Based Access Control (RBAC)** - Fine-grained permission management
- **Auto Logout** - Automatic session timeout
- **Protected Routes** - Routes guarded by auth status and role requirements

### 📊 Dashboard

- **Overview Statistics** - Key metrics and charts
- **Project Management** - View, create, and manage projects
- **Real-time Updates** - Live project status and activity

### 👥 User & Roles Management

- **User Management** - Create, edit, delete internal users
- **Role Management** - Define roles and permissions per team
- **Customer Management** - Manage external client organizations
- **Team Association** - Organize users and roles by team

### 🚀 Project Management

- **Project Workflow** - Visualize and manage project stages
- **Stage Management** - Define workflow stages
- **Stage Activities** - Add activities to each stage
- **Chapter Management** - Create and manage project chapters
- **Document Editor** - Rich text editing with TipTap
- **File Upload** - Bulk upload documents

### 🎨 UI & UX

- **Dark/Light Theme** - Toggle between themes
- **Responsive Design** - Works on desktop and mobile
- **Toast Notifications** - User feedback system
- **Data Tables** - Sortable, filterable tables with TanStack
- **Modal Dialogs** - Confirmation and data entry modals
- **Loading States** - Spinners and placeholders

## Project Structure

```
frontend/
├── src/
│   ├── pages/                    # Page components
│   │   ├── LoginPage.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Clients.tsx
│   │   ├── ClientProjects.tsx
│   │   ├── ProjectWorkflow.tsx
│   │   ├── Settings.tsx
│   │   ├── ChapterDetailPage.tsx
│   │   └── ...
│   │
│   ├── components/               # Reusable components
│   │   ├── ui/                  # Radix UI wrappers
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── ...
│   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   ├── Topbar.tsx           # Top navigation bar
│   │   ├── ThemeSwitcher.tsx    # Dark/light theme toggle
│   │   ├── ProtectedRoute.tsx   # Auth guard wrapper
│   │   ├── RoleGuard.tsx        # RBAC guard wrapper
│   │   ├── DocxViewer.tsx       # Document viewer
│   │   └── ...
│   │
│   ├── api/                      # API client functions
│   │   ├── client.ts            # Axios instance configuration
│   │   ├── auth.ts              # Authentication endpoints
│   │   ├── users.ts             # User endpoints
│   │   ├── clients.ts           # Client endpoints
│   │   ├── projects.ts          # Project endpoints
│   │   ├── stages.ts            # Stage endpoints
│   │   ├── workflows.ts         # Workflow endpoints
│   │   ├── chapters.ts          # Chapter endpoints
│   │   ├── uploads.ts           # File upload endpoints
│   │   └── ...
│   │
│   ├── store/                    # Zustand state management
│   │   ├── useAuthStore.ts      # Authentication state
│   │   ├── useThemeStore.ts     # Theme state (dark/light)
│   │   ├── useSidebarStore.ts   # Sidebar state
│   │   └── useToastStore.ts     # Toast notifications
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAutoLogout.ts     # Auto logout timer
│   │   ├── useRBAC.ts           # Role-based access control
│   │   └── ...
│   │
│   ├── layouts/                  # Layout components
│   │   └── AppLayout.tsx        # Main app layout with sidebar
│   │
│   ├── routes/                   # Route definitions
│   │   └── index.tsx            # All route configurations
│   │
│   ├── theme/                    # Theme configuration
│   │   ├── themes.ts            # Color schemes
│   │   └── applyTheme.ts        # Theme application logic
│   │
│   ├── utils/                    # Utility functions
│   │   └── cn.ts                # Class name merge utility
│   │
│   ├── config/                   # Configuration
│   │   └── fileManagerConfig.ts # File upload settings
│   │
│   ├── App.tsx                   # Root component
│   └── main.tsx                  # Entry point
│
├── index.html                    # HTML template
├── vite.config.ts               # Vite configuration
├── tsconfig.json                # TypeScript configuration
├── package.json                 # Dependencies
└── tailwind.config.ts           # Tailwind CSS configuration
```

## Technology Stack

### Core
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server

### Styling & UI
- **Tailwind CSS 4** - Utility-first CSS framework
- **Radix UI** - Unstyled, accessible component library
- **Lucide React** - Icon library
- **Class Variance Authority** - Type-safe component variants

### State Management
- **Zustand** - Lightweight state management
- **Axios** - HTTP client

### Routing
- **React Router 7** - Client-side routing

### Rich Text & Documents
- **TipTap** - Rich text editor
- **Mammoth** - DOCX to HTML converter

### Data Visualization
- **Recharts** - Chart library
- **TanStack React Table** - Headless table library

### Development
- **TypeScript 6** - Type checking
- **ESLint** - Code linting
- **Vite Plugins** - React refresh, Tailwind CSS

## Key Pages

### Authentication
- **LoginPage** - User login with email/password
- **ForgotPasswordPage** - Password reset

### Main Application
- **Dashboard** - Overview with statistics and quick actions
- **Clients** - List and manage external clients
- **ClientProjects** - View projects for a specific client

### Project Management
- **ProjectWorkflow** - Visual workflow stage management
- **ProjectPlanningPage** - Plan and organize project stages
- **ChapterDetailPage** - View chapter information
- **ChapterEditorPage** - Edit chapter content with rich text editor
- **ChapterFilePage** - Manage chapter documents

### Settings & Administration
- **UserManagement** - Manage internal system users
- **RolesManagement** - Define and manage roles
- **CustomerManagement** - Manage client organizations
- **WorkflowManagement** - Define workflow templates
- **StageManagement** - Create and configure stages

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`.

### Base Configuration
```typescript
// src/api/client.ts
const baseURL = "http://localhost:8000";
```

### API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/auth/login` | User authentication |
| `GET` | `/users` | List users |
| `POST` | `/users` | Create user |
| `GET` | `/roles` | List roles |
| `POST` | `/roles` | Create role |
| `GET` | `/clients` | List clients |
| `POST` | `/clients` | Create client |
| `GET` | `/projects` | List projects |
| `POST` | `/projects` | Create project |
| `GET` | `/stages` | List workflow stages |
| `POST` | `/chapters` | Create chapter |
| `POST` | `/upload` | Upload files |

## State Management (Zustand)

### useAuthStore
```typescript
// Authentication state
- user: User object
- token: JWT token
- isAuthenticated: Boolean
- login(email, password): Promise
- logout(): void
```

### useThemeStore
```typescript
// Theme state
- theme: 'light' | 'dark'
- toggleTheme(): void
```

### useToastStore
```typescript
// Notification state
- addToast(message, type): void
- removeToast(id): void
```

### useSidebarStore
```typescript
// Sidebar state
- isOpen: Boolean
- toggle(): void
```

## Hooks

### useAutoLogout
Auto logout after 30 minutes of inactivity:
```typescript
useAutoLogout();
```

### useRBAC
Check user permissions:
```typescript
const { hasRole, hasPermission } = useRBAC();
const isAdmin = hasRole('admin');
```

## Styling

### Tailwind CSS
Built with Tailwind CSS utility classes. Configuration in `tailwind.config.ts`.

### Dark/Light Theme
- Toggle in top-right corner
- Stored in browser localStorage
- Auto-applies to all components

### Component Library
UI components use Radix UI as the base, styled with Tailwind CSS.

## Environment Setup

The frontend expects the backend API at:
```
http://localhost:8000
```

To change this, modify `src/api/client.ts`:
```typescript
const baseURL = "http://your-api-url";
```

## Development Commands

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimizations

- **Code Splitting** - Route-based lazy loading
- **Image Optimization** - Responsive images
- **Tree Shaking** - Unused code removal
- **CSS Minification** - Optimized stylesheets

## Troubleshooting

### API Connection Failed
**Error:** `Failed to connect to http://localhost:8000`
- **Solution:** Ensure backend is running: `uvicorn main:app --reload`

### Authentication Issues
**Error:** `401 Unauthorized`
- **Solution:** Login again or check if token expired

### Page Not Loading
**Error:** White screen or blank page
- **Solution:** 
  1. Check browser console for errors (F12)
  2. Check network tab for failed API calls
  3. Clear browser cache (Ctrl+Shift+Delete)

### Styling Issues
**Error:** Tailwind styles not applying
- **Solution:** 
  1. Ensure Tailwind CSS is compiled: `npm run build`
  2. Clear browser cache
  3. Check `tailwind.config.ts` configuration

## File Upload Configuration

Configure file upload limits in `src/config/fileManagerConfig.ts`:
```typescript
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.xlsx'];
```

## Contributing

1. Create a feature branch
2. Make changes
3. Run `npm run lint` to check code style
4. Test thoroughly
5. Create a pull request

---

**Status:** ✅ React 19 | ✅ TypeScript | ✅ Tailwind CSS | ✅ RBAC | ✅ Dark/Light Theme | ✅ API Integration
