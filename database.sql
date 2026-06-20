-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: nexthome
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_id` int NOT NULL,
  `sender_id` int NOT NULL,
  `receiver_id` int NOT NULL,
  `message` text NOT NULL,
  `reply` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `property_id` (`property_id`),
  KEY `sender_id` (`sender_id`),
  KEY `receiver_id` (`receiver_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`id`) ON DELETE CASCADE,
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (4,10,1,3,'hello','hello','2026-06-20 09:19:48'),(5,24,1,6,'more detalis','aaaa','2026-06-20 09:45:06');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_id` int NOT NULL,
  `seller_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL DEFAULT '3000.00',
  `payment_status` varchar(20) NOT NULL DEFAULT 'completed',
  `paid_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `property_id` (`property_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (2,22,3,3000.00,'completed','2026-06-20 09:30:11'),(3,23,6,3000.00,'completed','2026-06-20 09:43:29'),(4,24,6,3000.00,'completed','2026-06-20 09:44:03'),(5,25,6,3000.00,'completed','2026-06-20 09:44:25');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `properties`
--

DROP TABLE IF EXISTS `properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `properties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `seller_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `price` decimal(15,2) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `contact_phone` varchar(20) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `plan` varchar(50) DEFAULT 'basic',
  `status` varchar(50) DEFAULT 'pending',
  `expiry_date` date DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `edit_count` int DEFAULT '0',
  `package` varchar(50) DEFAULT 'basic',
  PRIMARY KEY (`id`),
  KEY `seller_id` (`seller_id`),
  CONSTRAINT `properties_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `properties`
--

LOCK TABLES `properties` WRITE;
/*!40000 ALTER TABLE `properties` DISABLE KEYS */;
INSERT INTO `properties` VALUES (10,3,'Luxury 2 Bedroom Apartment for Sale in Colombo 05','A well-maintained luxury apartment located in the heart of Colombo 05. The apartment features 2 spacious bedrooms, 2 bathrooms, a modern kitchen, a comfortable living area, and a private balcony with city views. Conveniently located near schools, hospitals, supermarkets, and restaurants.',18500000.00,'Colombo 05','0719876543','House','basic','Approved','2026-07-02','20260618152701_image-1.jpg',0,'basic'),(11,3,'Residential Land for Sale in Gampaha','Valuable residential land located in a peaceful and rapidly developing area in Gampaha. The property is ideal for building a family home and has easy access to schools, banks, supermarkets, and public transportation. Clear deeds and all necessary facilities are available nearby.',5500000.00,'Gampaha','0712345678','House','basic','Approved','2026-07-02','20260618153729_lande.jpeg',0,'basic'),(21,3,'Modern 3 Bedroom House for Sale in Malabe','Beautiful modern house located in a peaceful residential area in Malabe. The property consists of 3 bedrooms, 2 bathrooms, a spacious living room, dining area, kitchen, and vehicle parking space. Close to schools, supermarkets, and public transport facilities.',25000000.00,'Malabe','0771234567','House','basic','Approved','2026-07-04','20260620145355_images_1.jpeg',0,'basic'),(22,3,'Luxury Villa for Sale in Negombo','A stunning luxury villa situated in a highly desirable residential area in Negombo. This spacious property features 4 large bedrooms, 3 modern bathrooms, a stylish living area, dining room, fully fitted kitchen, landscaped garden, swimming pool, and secure parking for multiple vehicles. Located close to the beach, schools, supermarkets, and other essential amenities. Ideal for families looking for comfort and elegance',85000000.00,'Negombo','0774567890','House','premium','Approved','2026-07-20','20260620145857_image-2.jpg',0,'premium'),(23,6,'Luxury 5 Bedroom House for Sale in Colombo 07','An elegant luxury house located in a prestigious residential area of Colombo 07. This premium property features 5 spacious bedrooms, 4 modern bathrooms, a large living and dining area, a fully equipped kitchen, landscaped garden, swimming pool, and secure parking for multiple vehicles. The house is situated close to leading schools, hospitals, shopping centers, and other essential facilities. Perfect for families seeking comfort, convenience, and a high-end lifestyle.',75000000.00,'Colombo 07','0771234567','House','premium','Approved','2026-07-20','20260620150544_1.jpg',0,'premium'),(24,6,'Modern House for Sale in Kandy','A beautifully designed modern house situated in a peaceful and highly sought-after area in Kandy. This premium property offers spacious living areas, elegant interiors, and excellent outdoor space. The house is ideal for families looking for a comfortable and luxurious lifestyle with easy access to schools, supermarkets, hospitals, and public transport.',60000000.00,'Kandy','0712345678','House','premium','Approved','2026-07-20','20260620150915_kandy_house.jpeg',0,'premium'),(25,6,'Luxury 4 Bedroom House for Sale in Nugegoda','A modern luxury house located in a prime residential area of Nugegoda. The property features spacious bedrooms, stylish bathrooms, a large living room, modern kitchen, landscaped garden, swimming pool, and secure parking. Close to schools, supermarkets, hospitals, and public transport facilities.',50000000.00,'Nugegoda','0776543210','House','premium','Approved','2026-07-20','20260620151205_kandy_house1.jpg',0,'premium');
/*!40000 ALTER TABLE `properties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','seeker','seller') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Pahan Athukorala','pahan123@gmail.com','1234','seeker','2026-04-08 14:26:06','active'),(2,'gayashani','gayashani@gmail.com','gayashani123','seeker','2026-04-08 15:25:18','active'),(3,'Ashen perera','ashen@gmail.com','Ashen123','seller','2026-04-16 11:09:58','active'),(6,'Kavee Perera','kavee@gmail.com','Kavee123','seller','2026-06-05 01:41:50','active');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-20 16:33:09
