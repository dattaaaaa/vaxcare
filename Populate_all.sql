-- Add Vaccines
INSERT INTO Vaccines (name, description, min_age, max_age) VALUES
('Bacillus Calmette Guerin (BCG)', 'Administered at birth or as early as possible till one year of age. Dose: 0.1ml (0.05ml until 1 month age). Route: Intra-dermal. Site: Left Upper Arm.', 0, 12),
('Oral Polio Vaccine (OPV)-0', 'Administered at birth or as early as possible within the first 15 days. Dose: 2 drops. Route: Oral.', 0, 0),
('Hepatitis B birth dose', 'Administered at birth or as early as possible within 24 hours. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 0, 0),
('Oral Polio Vaccine (OPV)-1', 'Administered at 6 weeks. Dose: 2 drops. Route: Oral.', 6, 6),
('Pentavalent-1', 'Administered at 6 weeks. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 2, 3),
('Rotavirus Vaccine (RVV)-1', 'Administered at 6 weeks. Dose: 5 drops (liquid vaccine) or 2.5 ml (lyophilized vaccine). Route: Oral.', 2, 3),
('Fractional dose of Inactivated Polio Vaccine (fIPV)-1', 'Administered at 6 weeks. Dose: 0.1 ml. Route: Intra-dermal. Site: Right upper arm.', 2, 3),
('Pneumococcal Conjugate Vaccine (PCV)-1', 'Administered at 6 weeks. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 2, 3),
('Oral Polio Vaccine (OPV)-2', 'Administered at 10 weeks. Dose: 2 drops. Route: Oral.', 3, 4),
('Pentavalent-2', 'Administered at 10 weeks. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 3, 4),
('Rotavirus Vaccine (RVV)-2', 'Administered at 10 weeks. Dose: 5 drops (liquid vaccine) or 2.5 ml (lyophilized vaccine). Route: Oral.', 3, 4),
('Oral Polio Vaccine (OPV)-3', 'Administered at 14 weeks. Dose: 2 drops. Route: Oral.', 4, 5),
('Pentavalent-3', 'Administered at 14 weeks. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 4, 5),
('Fractional dose of Inactivated Polio Vaccine (fIPV)-2', 'Administered at 14 weeks. Dose: 0.1 ml. Route: Intra-dermal. Site: Right upper arm.', 4, 5),
('Rotavirus Vaccine (RVV)-3', 'Administered at 14 weeks. Dose: 5 drops (liquid vaccine) or 2.5 ml (lyophilized vaccine). Route: Oral.', 4, 5),
('Pneumococcal Conjugate Vaccine (PCV)-2', 'Administered at 14 weeks. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 4, 5),
('Measles & Rubella (MR)-1', 'Administered at 9-12 months. Dose: 0.5 ml. Route: Sub-cutaneous. Site: Right upper arm.', 9, 12),
('Japanese Encephalitis (JE)-1', 'Administered at 9-12 months in endemic districts. Dose: 0.5 ml. Route: Sub-cutaneous or Intramuscular. Site: Left upper arm (live vaccine) or Antero-lateral mid-thigh (killed vaccine).', 9, 12),
('Pneumococcal Conjugate Vaccine (PCV)-Booster', 'Administered at 9-12 months. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 9, 12),
('MR-2', 'Administered at 16-24 months. Dose: 0.5 ml. Route: Sub-cutaneous. Site: Right upper arm.', 16, 24),
('DPT-Booster-1', 'Administered at 16-24 months. Dose: 0.5 ml. Route: Intra-muscular. Site: Antero-lateral side of mid-thigh.', 16, 24),
('OPV Booster', 'Administered at 16-24 months. Dose: 2 drops. Route: Oral.', 16, 24),
('JE-2', 'Administered at 16-24 months in endemic districts. Dose: 0.5 ml. Route: Sub-cutaneous or Intramuscular. Site: Left upper arm (live vaccine) or Antero-lateral mid-thigh (killed vaccine).', 16, 24),
('Vitamin A (2nd to 9th dose)', 'Administered every 6 months starting from 16-18 months until age 5 years. Dose: 2 ml (2 lakh IU). Route: Oral.', 16, 60),
('DPT-Booster-2', 'Administered at 5-6 years. Dose: 0.5 ml. Route: Intra-muscular. Site: Upper Arm.', 60, 72),
('Td', 'Administered at 10 years and 16 years. Dose: 0.5 ml. Route: Intra-muscular. Site: Upper arm.', 120, 192);

-- Populate rest of the tables 
-- 1. Users Table (10 tuples)
INSERT INTO Users (email, password) VALUES
('raj.kumar@gmail.com', SHA2('password123', 256)),
('priya.sharma@yahoo.com', SHA2('secure456', 256)),
('amit.patel@outlook.com', SHA2('pass789', 256)),
('deepa.nair@gmail.com', SHA2('deep123', 256)),
('sandeep.reddy@yahoo.com', SHA2('sandy456', 256)),
('meera.singh@gmail.com', SHA2('meera789', 256)),
('karthik.krishnan@outlook.com', SHA2('kart123', 256)),
('anita.desai@yahoo.com', SHA2('anita456', 256)),
('vikram.mehta@gmail.com', SHA2('vik789', 256)),
('lakshmi.iyer@outlook.com', SHA2('lak123', 256));

-- 2. Profiles Table (2-3 profiles per user)
INSERT INTO Profiles (gender, fname, mname, lname, age, user_id) VALUES

('Male', 'Raj', '', 'Kumar', 35, 1),
('Female', 'Anjali', '', 'Kumar', 32, 1),
('Female', 'Riya', '', 'Kumar', 5, 1),


('Female', 'Priya', '', 'Sharma', 28, 2),
('Male', 'Arun', '', 'Sharma', 30, 2),


('Male', 'Amit', '', 'Patel', 40, 3),
('Female', 'Neha', '', 'Patel', 38, 3),
('Male', 'Dev', '', 'Patel', 3, 3),

('Female', 'Deepa', '', 'Nair', 29, 4),
('Male', 'Arjun', '', 'Nair', 2, 4),

('Male', 'Sandeep', '', 'Reddy', 45, 5),
('Female', 'Kavita', '', 'Reddy', 40, 5),
('Female', 'Sonia', '', 'Reddy', 4, 5),

('Female', 'Meera', '', 'Singh', 33, 6),
('Male', 'Rohan', '', 'Singh', 1, 6),

('Male', 'Karthik', '', 'Krishnan', 37, 7),
('Female', 'Divya', '', 'Krishnan', 35, 7),
('Male', 'Aditya', '', 'Krishnan', 6, 7),

('Female', 'Anita', '', 'Desai', 31, 8),
('Male', 'Rahul', '', 'Desai', 2, 8),

('Male', 'Vikram', '', 'Mehta', 42, 9),
('Female', 'Pooja', '', 'Mehta', 38, 9),
('Male', 'Vivaan', '', 'Mehta', 4, 9),

('Female', 'Lakshmi', '', 'Iyer', 36, 10),
('Male', 'Krishna', '', 'Iyer', 3, 10);

-- 3. VaccineCentres Table (20 locations in Bangalore)
INSERT INTO VaccineCentres (name, address, district, pincode) VALUES
('Indiranagar Health Center', '100 Feet Road, HAL 2nd Stage', 'Indiranagar', '560038'),
('Koramangala PHC', '80 Feet Road, 4th Block', 'Koramangala', '560034'),
('Jayanagar General Hospital', '9th Block, 40th Cross', 'Jayanagar', '560041'),
('JP Nagar Health Center', '24th Main, Phase 6', 'JP Nagar', '560078'),
('Whitefield Medical Center', 'ITPL Main Road', 'Whitefield', '560066'),
('Malleswaram Clinic', '8th Cross, Sampige Road', 'Malleswaram', '560003'),
('HSR Layout PHC', 'Sector 2, 27th Main', 'HSR Layout', '560102'),
('BTM Layout Health Center', '16th Main, 2nd Stage', 'BTM Layout', '560076'),
('Banashankari Hospital', '50 Feet Road, 3rd Stage', 'Banashankari', '560085'),
('Yelahanka New Town Clinic', 'Main Road, Sector A', 'Yelahanka', '560064'),
('RT Nagar Health Center', '5th Block Main Road', 'RT Nagar', '560032'),
('Hebbal PHC', 'Ring Road Junction', 'Hebbal', '560024'),
('Electronic City Hospital', 'Phase 1, Main Road', 'Electronic City', '560100'),
('Marathahalli Clinic', 'Outer Ring Road', 'Marathahalli', '560037'),
('Bannerghatta Health Center', 'BG Road, JP Nagar 8th Phase', 'Bannerghatta', '560083'),
('CV Raman Nagar PHC', 'Main Road, AECS Layout', 'CV Raman Nagar', '560093'),
('Rajajinagar Hospital', '1st Block, Chord Road', 'Rajajinagar', '560010'),
('KR Puram Health Center', 'Old Madras Road', 'KR Puram', '560036'),
('Basavanagudi PHC', 'Gandhi Bazaar Main Road', 'Basavanagudi', '560004'),
('Vijayanagar Medical Center', 'Metro Station Road', 'Vijayanagar', '560040');

-- 4. Inventory Table (30 tuples, each with a single vaccine)
INSERT INTO Inventory (expiration_date, quantity) VALUES
('2025-12-31', 100),
('2025-12-31', 150),
('2025-12-31', 200),
('2025-12-31', 120),
('2025-12-31', 180),
('2025-12-31', 90),
('2025-12-31', 160),
('2025-12-31', 140),
('2025-12-31', 110),
('2025-12-31', 170),
('2025-06-30', 130),
('2025-06-30', 190),
('2025-06-30', 150),
('2025-06-30', 120),
('2025-06-30', 140),
('2025-06-30', 160),
('2025-06-30', 180),
('2025-06-30', 200),
('2025-06-30', 170),
('2025-06-30', 130),
('2025-03-31', 150),
('2025-03-31', 140),
('2025-03-31', 160),
('2025-03-31', 180),
('2025-03-31', 120),
('2025-03-31', 190),
('2025-03-31', 140),
('2025-03-31', 170),
('2025-03-31', 150),
('2025-03-31', 130);

-- 5. Schedules Table (10 tuples)
INSERT INTO Schedules (date, dose_number, centre_id) VALUES
('2025-01-15', 1, 1),
('2025-01-15', 2, 2),
('2025-01-16', 1, 3),
('2025-01-16', 2, 4),
('2025-01-17', 1, 5),
('2025-01-17', 2, 6),
('2025-01-18', 1, 7),
('2025-01-18', 2, 8),
('2025-01-19', 1, 9),
('2025-01-19', 2, 10);

-- 6. Includes Table (Vaccines ↔ Schedules)
INSERT INTO Includes (vaccine_id, schedule_id) VALUES
(1, 1), (2, 1), (3, 1),
(4, 2), (5, 2), (6, 2),
(7, 3), (8, 3), (9, 3),
(10, 4), (11, 4), (12, 4),
(13, 5), (14, 5), (15, 5),
(16, 6), (17, 6), (18, 6),
(19, 7), (20, 7), (21, 7),
(22, 8), (23, 8), (24, 8),
(25, 9), (1, 9), (2, 9),
(3, 10), (4, 10), (5, 10);

-- 7. AvailableAt Table (Vaccines ↔ VaccineCentres)
INSERT INTO AvailableAt (vaccine_id, centre_id)
SELECT v.vaccine_id, vc.centre_id
FROM Vaccines v
CROSS JOIN VaccineCentres vc
WHERE vc.centre_id <= 10;

-- 8. StoredAt Table (Vaccines ↔ Inventory)
INSERT INTO StoredAt (inventory_id, vaccine_id)
SELECT inventory_id, 
       1 + (inventory_id % (SELECT COUNT(*) FROM Vaccines))
FROM Inventory;

-- 9. Appointments Table (20 tuples)
INSERT INTO Appointments (appointment_date, time_slot, vaccine_id, profile_id, schedule_id) VALUES
('2025-01-15', '09:00:00', 1, 3, 1),
('2025-01-15', '09:30:00', 2, 8, 1),
('2025-01-15', '10:00:00', 3, 10, 1),
('2025-01-15', '10:30:00', 4, 14, 2),
('2025-01-16', '09:00:00', 5, 19, 3),
('2025-01-16', '09:30:00', 6, 21, 3),
('2025-01-16', '10:00:00', 7, 25, 4),
('2025-01-16', '10:30:00', 8, 2, 4),
('2025-01-17', '09:00:00', 9, 4, 5),
('2025-01-17', '09:30:00', 10, 6, 5),
('2025-01-17', '10:00:00', 11, 11, 6),
('2025-01-17', '10:30:00', 12, 13, 6),
('2025-01-18', '09:00:00', 13, 15, 7),
('2025-01-18', '09:30:00', 14, 17, 7),
('2025-01-18', '10:00:00', 15, 20, 8),
('2025-01-18', '10:30:00', 16, 22, 8),
('2025-01-19', '09:00:00', 17, 24, 9),
('2025-01-19', '09:30:00', 18, 5, 9),
('2025-01-19', '10:00:00', 19, 7, 10),
('2025-01-19', '10:30:00', 20, 9, 10);