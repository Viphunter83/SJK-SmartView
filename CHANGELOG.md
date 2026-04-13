# Changelog - SJK SmartView

## [0.2.0] - 2026-04-13
### Added
- **Firebase Authentication:** Global `AuthContext`, `ProtectedRoute` wrapper, and full Login flow integration via Client SDK.
- **Firebase Storage:** Integrated `StorageService` using Firebase Admin SDK and `service_account.json` for cloud-based image management.
- **Vietnam Localization:** Re-seeded database with 6 real SJK Group locations in HCMC and Hanoi with valid images from `shojiki.vn`.
- **Global Providers:** Centralized `AuthProvider`, `SidebarProvider`, and `TooltipProvider` in root layout.
- **Toaster:** Added `shadcn/ui` Toaster for real-time authentication feedback.

### Fixed
- **Dead UI Bug:** Removed redundant `SidebarProvider` which was blocking all interactive events.
- **Hydration Mismatch:** Resolved React hydration errors in `MockupCreator` using mount checks.
- **Catalog Image Recovery:** Fixed image rendering in `LocationCatalog` to handle both local and absolute URLs + added error fallbacks.
- **Docker Sync:** Corrected backend seed execution path within containers.

### Changed
- Refactored `LoginPage` from mock logic to real Firebase Auth.
- Updated `LocationCatalog` to display real-world Vietnam data instead of Moscow placeholders.
- Header user display now dynamically shows the email of the logged-in manager.

## [0.1.0] - 2026-04-13
### Added
- **Project Structure:** Initialized monorepo with `frontend/` (Next.js 15) and `backend/` (FastAPI).
- **Architecture Docs:** Created `detailed_design.md`, `implementation_plan.md`, and `business_logic.md`.
- **UI Components:**
  - Sidebar with navigation and glassmorphism.
  - `LocationCatalog` with search, filtering, and screen cards.
  - `MockupCreator` modal with file upload and AI-processing simulation.
- **Backend API:**
  - `/v1/mockup/generate` endpoint for multipart image uploads.
  - Pydantic schemas for API consistency.
  - Mock integration with Modal.com logic.
- **AI Infrastructure:**
  - `worker.py` script for Modal.com with Perspective Warp (homography) logic using OpenCV.
- **Database:**
  - Initial PostgreSQL schema for Users, Locations, and Mockups.
  - Moved migrations to `database/migrations/`.
- **Infrastructure & DevOps:**
  - Full Dockerization: `Dockerfile` for backend/frontend and `docker-compose.yml`.
  - Local PostgreSQL container for development.
  - Git initialization and `.gitignore` setup.
  - Cloud deployment readiness (Vercel & Railway via `railway.json`).
- **Assets:**
  - Created `tests/assets/screens/` directory for test data.

### Changed
- Switched backend Python version to **3.12** for stability and performance.
- Replaced Supabase-specific dependencies with standard PostgreSQL.
- Updated project pathing to handle monorepo structure in Docker.

### Fixed
- Missing `ImageIcon` import in `mockup-creator.tsx`.
- Missing OpenCV dependencies in the backend Docker image.
