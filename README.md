# ⚙️ Anyadaan Backend — Powering Transparent Donations

The **Anyadaan Backend** is the core engine that powers the Anyadaan platform.  
It handles **authentication, donation workflows, NGO coordination, notifications, and data integrity**, ensuring every donation is **traceable, secure, and impactful**.

---

## 🧠 Purpose

This backend exists to solve one major problem:

> *How do we make donations trustworthy, fast, and verifiable at scale?*

Anyadaan’s backend ensures **real-time coordination** between donors and NGOs while maintaining **data transparency and security**.

---

## 🚀 Core Responsibilities

- User authentication & role management
- Donation lifecycle management
- NGO & volunteer coordination
- Email notification system
- Secure API layer for frontend & mobile apps
- Admin monitoring & moderation

---

## 🏗️ Architecture Overview

Client (Web / Mobile)
↓
REST API (Flask)
↓
Business Logic Layer
↓
Database (PostgreSQL / MongoDB)
↓
Notification Services (Email)



---

## 🔑 Key Features

### 👤 Role-Based Access Control (RBAC)
- **Donor**
- **NGO / Volunteer**
- **Admin**

Each role has clearly defined permissions enforced at API level.

---

### 🍲 Food Donation Workflow (Backend Logic)

1. Donor creates a food donation
2. Donation is stored with status: `PENDING`
3. NGOs/Volunteers are notified via email
4. First acceptor locks the donation
5. Status updates → `ACCEPTED → COMPLETED`
6. Full audit trail is maintained

---

### 💸 Monetary Donation Handling *(Planned)*

- Transaction validation
- Donation-to-NGO mapping
- Secure record storage
- Payment gateway integration (future)

---

### 📧 Notification Engine

- Email alerts for:
  - New donation creation
  - Donation acceptance
  - Completion confirmation
- Fail-safe retry logic *(planned)*

---

### 🧾 Transparency & Logging

- Timestamped records
- Status change history
- Admin-level access to logs
- Tamper-resistant donation states

---

## 🛠️ Tech Stack

### Backend
- **Python**
- **Flask**
- Flask-RESTful
- Flask-JWT / Token-based auth

### Database
- PostgreSQL / MongoDB
- SQLAlchemy / ODM

### Communication
- SMTP / EmailJS
- REST APIs (JSON)

### Infrastructure *(Planned)*
- Docker
- Nginx
- CI/CD Pipelines
- Rate limiting & API security

---

