# NextHome - Real Estate Platform

NextHome is a web-based Real Estate platform built using Python (Flask) and MySQL. The platform allows property owners and agents (Sellers) to publish advertisements for houses and lands, while enabling property buyers (Seekers) to browse through active listings and send direct inquiries to the sellers.

## 🚀 Features

### 👨‍💼 Seller Dashboard
- **Property Listings:** Add and organize property listings categorized by type (House or Land).
- **Flexible Image Upload:** Ability to upload either 3 or 6 images depending on the chosen listing plan.
- **Inquiry Notification & Reply:** View the real-time count of incoming inquiries from buyers directly on the dashboard and reply instantly using a popup modal.
- **Listing Expiry & Auto-Delete:** Automated house-keeping system that permanently deletes listings from the system once their plan duration expires (14 or 30 days).

### 🔍 Seeker / Buyer Flow
- **Location & Type Filter:** Effortlessly search and filter properties based on location/city and type (House/Land).
- **View Details:** View a dedicated details page for each property showcasing comprehensive descriptions, features, and uploaded images.
- **Instant Inquiry:** Contact sellers directly through the platform via an instant message inquiry system.

### 🛡️ Admin Panel
- **Approval System:** A moderation queue allowing administrators to review, approve, or reject property posts (both Basic and Premium) before they go live on the website.

---

## 💰 Pricing & Listing Plans

The platform offers two primary tiers for publishing property advertisements:

### 1. Basic Plan (Free)
- **Price:** 100% Free.
- **Image Limit:** Maximum of 3 images can be uploaded.
- **Validity:** Valid for 14 days, after which the post is automatically deleted by the system.
- **Workflow:** Once the seller submits the listing, it enters the admin moderation queue. As soon as the Admin approves it, the listing instantly goes live/published on the website.

### 2. Premium Plan (Featured)
- **Price:** LKR 3,000/= per listing.
- **Image Limit:** Allows up to 6 high-quality images for a more detailed showcase.
- **Validity:** Displayed prominently in the "Premium Featured Properties" section for 30 days, after which it is automatically deleted.
- **Workflow:** After submission, the post must first be reviewed and approved by the Admin. Once approved, the payment option becomes available to the seller. The listing is published and goes live only after the successful completion of the LKR 3,000 payment.

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask Framework)
- **Database:** MySQL Workbench
- **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome (for Icons)
- **Key Libraries:** `flask_mysqldb` (Database connection), `werkzeug` (Secure file & image uploads)

---

