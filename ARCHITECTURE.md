# 🏗️ Intelligent User Management Chatbot - Architecture & Technical Documentation

This document provides a comprehensive technical overview and architectural specification of the **User Management Chatbot Application**.

---

## 🚀 Executive Overview

The application is a full-stack, web-based intelligent chatbot system built with **Python (Flask)**, **SQLite**, **HTML5/JS**, and custom **Vanilla CSS Glassmorphic Styling**. 

It transitions basic CRUD user operations into a natural language conversational interface backed by real-time state synchronization between the database and the client UI.

---

## 📐 System Architecture Diagram

```mermaid
graph TD
    Client[🖥️ Web Browser UI] -->|HTTP POST /login| AuthModule[🔐 Auto-Login Engine]
    Client -->|HTTP POST /message| NLPEngine[🤖 NLP Command Parser]
    Client -->|HTTP GET /api/users| APILayer[⚡ REST API Layer]
    
    subgraph Flask Backend (app.py)
        AuthModule --> SessionMgr[Session Store]
        NLPEngine --> IntentParser[Intent & Regex Evaluator]
        IntentParser --> UserMatcher[Fuzzy User Matcher]
    end

    subgraph Data Storage
        UserMatcher -->|SQL Queries| DB[(💾 SQLite Database: users.db)]
        APILayer -->|SQL SELECT| DB
    end

    subgraph User Interface (Templates & CSS)
        UI_Login[login.html]
        UI_Dash[index.html]
        UI_CSS[style.css - Glassmorphism System]
    end
```

---

## 📂 Project Structure

```
Task_chatbot Vibe/
├── app.py                  # Main Flask App & NLP Command Engine
├── users.db                # SQLite Persistent Database
├── Readme                  # Quickstart Guide
├── ARCHITECTURE.md         # Full System Architecture & Tech Spec
├── Templates/
│   ├── login.html          # Glassmorphic Auto-Login Interface
│   └── index.html          # Chatbot Dashboard & Live Sidebar UI
└── static/
    └── css/
        └── style.css       # Master Glassmorphic Design System
```

---

## 🔬 Core Components & Tech Stack

### 1. Backend Framework (`app.py`)
- **Language & Engine**: Python 3.x with Flask framework.
- **Session Security**: Cryptographic cookie session management (`app.secret_key`).
- **Database Helper**: SQLite3 wrapper with `Row` factory for dictionary-like column access.

### 2. Intelligent NLP Command Engine (`/message`)
The backend uses a pattern-matching natural language parser to identify user intents:

| Intent Category | Supported Phrasing Examples | Action / Logic |
| :--- | :--- | :--- |
| **Add User** | `can you add the user "john.smith@xyz.com" with phone number "+92332"` | Extracts email, phone, formats default name from email prefix (`John Smith`), checks duplicates, inserts record into SQLite. |
| **Update City** | `can you update samanthas city to Cordoba` | Uses fuzzy possessive matching (`samanthas` -> `Samantha`), updates city to `Cordoba` in DB. |
| **Update Phone** | `update john's phone to +92333` | Searches user by email or name, updates phone number in DB. |
| **Remove User** | `can you remove the user "john.smith@xyz.com"` | Finds user record by email or name, deletes from DB. |
| **Show Users** | `show users`, `list users` | Queries all users, formats output into JSON array for table rendering. |

### 3. Database Schema (`users.db`)

#### `users` Table Schema
```sql
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    city TEXT
);
```

#### Initial Seed Data:
- `Admin`: `jhon.smith@xyz.com` | Phone: `+92322` | City: `Lahore`
- `Samantha`: `samantha@xyz.com` | Phone: `+14155552671` | City: `Madrid`
- `Alex Johnson`: `alex.j@xyz.com` | Phone: `+447911123456` | City: `London`

---

## 🎨 Design System & UI Architecture (`style.css` & `index.html`)

### 1. Glassmorphism Design System
- **Colors**: Dark slate background (`#090d16`), Indigo/Cyan accent gradients (`linear-gradient(135deg, #6366f1, #06b6d4)`).
- **Glass Card Technique**: Translucent dark cards (`rgba(18, 26, 43, 0.65)`) with backdrop blur (`backdrop-filter: blur(16px)`).
- **Typography**: Google Font `Plus Jakarta Sans` for clean UI readability.

### 2. Live Database Synchronization Sidebar
- Loads current users list from `/api/users` on dashboard mount.
- Automatically re-fetches and updates the sidebar whenever the chatbot executes an `add`, `update`, or `remove` action.

### 3. Interactive Features
- **Quick-Login Chips**: One-click login on `/`.
- **Command Pill Chips**: Clickable sample commands in the chat sidebar.
- **Typing Indicator**: Animated 3-dot pulse indicator while waiting for bot server responses.
- **Rich Output Cards**: Formatted HTML response tables for listing users.

---

## 🔄 End-to-End Execution Flow Example

1. **User Request**: `can you update samanthas city to Cordoba`
2. **Client JS**: Sends `POST /message` payload `{ "message": "can you update samanthas city to Cordoba" }`.
3. **Flask Route `/message`**:
   - Matches `UPDATE` intent regex.
   - Invokes `find_user_by_identifier("samanthas")` which strips trailing `s`, finds `Samantha` (`samantha@xyz.com`).
   - Executes `UPDATE users SET city = 'Cordoba' WHERE id = 2`.
   - Returns JSON response: `{ "action": "user_updated", "reply": "✏️ Updated **Samantha**'s city to **Cordoba**.", "status": "success" }`.
4. **Client UI**:
   - Renders bot message bubble with formatted text.
   - Detects `data.action` presence and calls `loadLiveUsers()` API.
   - Sidebar instantly re-renders showing Samantha's updated city (`Cordoba`) without page reload.

---
*Created automatically for project documentation & presentation.*
