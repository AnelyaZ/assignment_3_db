DROP TABLE IF EXISTS APPOINTMENT CASCADE;
DROP TABLE IF EXISTS JOB_APPLICATION CASCADE;
DROP TABLE IF EXISTS JOB CASCADE;
DROP TABLE IF EXISTS ADDRESS CASCADE;
DROP TABLE IF EXISTS MEMBER CASCADE;
DROP TABLE IF EXISTS CAREGIVER CASCADE;
DROP TABLE IF EXISTS "USER" CASCADE;

CREATE TABLE "USER"(
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    given_name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    phone_number VARCHAR(25),
    profile_description TEXT,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE CAREGIVER(
    caregiver_user_id INT PRIMARY KEY REFERENCES "USER"(user_id) ON DELETE CASCADE,
    photo VARCHAR(255),
    gender VARCHAR(10),
    caregiving_type VARCHAR(50) NOT NULL CHECK (caregiving_type IN ('babysitter', 'caregiver for elderly', 'playmate for children')),
    hourly_rate DECIMAL(10,3)
);

CREATE TABLE MEMBER(
    member_user_id INT PRIMARY KEY REFERENCES "USER"(user_id) ON DELETE CASCADE,
    house_rules TEXT NOT NULL,
    dependent_description TEXT NOT NULL
);

CREATE TABLE ADDRESS (
    member_user_id INT PRIMARY KEY REFERENCES MEMBER(member_user_id) ON DELETE CASCADE,
    house_number VARCHAR(25) NOT NULL,
    street VARCHAR(150) NOT NULL,
    town VARCHAR(100) NOT NULL
);

CREATE TABLE JOB (
    job_id SERIAL PRIMARY KEY,
    member_user_id INT NOT NULL REFERENCES MEMBER(member_user_id) ON DELETE CASCADE,
    required_caregiving_type VARCHAR(50) NOT NULL CHECK (required_caregiving_type IN ('babysitter', 'caregiver for elderly', 'playmate for children')),
    other_requirements TEXT,
    date_posted DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE JOB_APPLICATION (
    caregiver_user_id INT NOT NULL REFERENCES CAREGIVER(caregiver_user_id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES JOB(job_id) ON DELETE CASCADE,
    date_applied DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (caregiver_user_id, job_id)
);

CREATE TABLE APPOINTMENT (
    appointment_id SERIAL PRIMARY KEY,
    caregiver_user_id INT NOT NULL REFERENCES CAREGIVER(caregiver_user_id) ON DELETE RESTRICT,
    member_user_id INT NOT NULL REFERENCES MEMBER(member_user_id) ON DELETE RESTRICT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    work_hours INT NOT NULL,
    status VARCHAR(25) NOT NULL CHECK (status IN ('pending', 'confirmed', 'declined'))
);


INSERT INTO "USER"(user_id, email, given_name, surname, city, phone_number, profile_description, password) VALUES
(1, 'arman@example.com','Arman','Armanov','Astana','+77770000001','Russian/Kazakh babysitter and math tutor','pwd1'),
(2, 'alina@example.com','Alina','Askarova','Atyrau','+77770000002','Full-time babysitter with 5 years experience, specializes in newborns','pwd2'),
(3, 'aisha@example.com','Aisha','Asetova','Almaty','+77770000003','Elderly caregiver and student in nursing','pwd3'),
(4, 'zhannur@example.com','Zhannur','Serikova','Kostanay','+77770000004','Energetic and creative playmate for children','pwd4'),
(5, 'nurlan@example.com','Nurlan','Nurlanov','Karaganda','+77770000005','Experienced nanny','pwd5'),
(6, 'laila@example.com','Laila','Sultanova','Astana','+77770000006','Educated babysitter with a background in psychology','pwd6'),
(7, 'zhuldyz@example.com','Zhuldyz','Yerlanova','Aktobe','+77770000007','Sits with elderly people','pwd7'),
(8, 'david@example.com','David','Peter','Oskemen','+77770000008','Babysitter and tutor','pwd8'),
(9, 'olga@example.com','Olga','Olegovna','Pavlodar','+77770000009','Companion for elders','pwd9'),
(10, 'kate@example.com','Kate','Smith','Almaty','+77770000010','Playmate for children. Native English speaker','pwd10'),
(11, 'ali@example.com','Ali','Armanov','Astana','+77770000011','Looking for a caregiver','pwd11'),
(12, 'amina@example.com','Amina','Aminova','Shymkent','+77770000012','Seeking a babysitter','pwd12'),
(13, 'aina@example.com','Aina','Talgat','Astana','+77770000013','Needs help with elderly father','pwd13'),
(14, 'dina@example.com','Dina','Talgatova','Almaty','+77770000014','Seeking playmate and tutor for a 6 y.o. boy','pwd14'),
(15, 'vika@example.com','Vika','Ivanova','Astana','+77770000015','Single mother seeking part-time sitter','pwd15'),
(16, 'beka@example.com','Beknur','Askar','Karaganda','+77770000016','Looking for weekend caregiver','pwd16'),
(17, 'aru@example.com','Aru','Amirova','Shymkent','+77770000017','Need a reliable babysitter for evening shifts','pwd17'),
(18, 'marina@example.com','Marina','Ivanova','Kostanay','+77770000018','Looking for nanny','pwd18'),
(19, 'ramazan@example.com','Ramazan','Rustemov','Almaty','+77770000019','Looking for experienced person, playmate for children','pwd19'),
(20, 'gulnara@example.com','Gulnara','Ruslanova','Shymkent','+77770000020','Need babysitter with flexible schedule','pwd20');

INSERT INTO CAREGIVER(caregiver_user_id, photo, gender, caregiving_type, hourly_rate) VALUES
(1, 'arm.jpg', 'Male', 'babysitter', 9.50),
(2, 'ali.jpg', 'Female', 'babysitter', 15.00),
(3, 'ais.jpg', 'Female', 'caregiver for elderly', 12.00),
(4, 'zha.jpg', 'Female', 'playmate for children', 18.00),
(5, 'nur.jpg', 'Male', 'babysitter', 9.90),
(6, 'lai.jpg', 'Female', 'babysitter', 20.00),
(7, 'zhu.jpg', 'Female', 'caregiver for elderly', 10.50),
(8, 'dav.jpg', 'Male', 'playmate for children', 16.00),
(9, 'olg.jpg', 'Female', 'caregiver for elderly', 22.00),
(10, 'kat.jpg', 'Female', 'playmate for children', 8.00);

INSERT INTO MEMBER (member_user_id, house_rules, dependent_description) VALUES
(11, 'No pets', 'Elderly grandfather'),
(12, 'No pets', '7 years old boy'),
(13, 'Prioritize hygiene for food and medicine', 'Elderly father'),
(14, 'No food or drinks in the living room', '1 child, 6 years old, high energy'),
(15, 'Quiet hours 1 PM to 3 PM. Avoid strong perfumes', '1 toddler, 2 years old'),
(16, 'Be soft-spoken and gentle. Double-check all medications', 'Elderly grandmother, hearing impaired'),
(17, 'Infant care only and no cooking', '1 newborn baby'),
(18, 'Play and cook for kids', '2 boys, 7 and 8 years old'),
(19, 'Lights off by 9PM', '2 children, 2 and 3 years old'),
(20, 'No outside snacks', '1 child, 7 years old');

INSERT INTO ADDRESS (member_user_id, house_number, street, town) VALUES
(11, '25', 'Turkestan street', 'Astana'),
(12, '15', 'Tole Bi street', 'Shymkent'),
(13, '8', 'Kabanbay Batyr street', 'Astana'),
(14, '22', 'Al-Farabi street', 'Almaty'),
(15, '7', 'Kabanbay Batyr street', 'Astana'),
(16, '33', 'Gagarin street', 'Karaganda'),
(17, '10', 'Central street', 'Shymkent'),
(18, '5', 'Kabanbay Batyr street', 'Kostanay'),
(19, '18', 'Kunaev street', 'Almaty'),
(20, '25', 'Ryskulov street', 'Shymkent');

INSERT INTO JOB (job_id, member_user_id, required_caregiving_type, other_requirements, date_posted) VALUES
(1, 12, 'babysitter', 'Evenings and weekends only. Must know English', '2025-10-20'),
(2, 12, 'playmate for children', 'Outdoor activities only', '2025-10-21'),
(3, 15, 'babysitter', 'Need help with kids for 3 hours', '2025-10-23'),
(4, 16, 'caregiver for elderly', 'Required for two hours daily, must be soft-spoken and patient', '2025-10-25'),
(5, 13, 'caregiver for elderly', 'Needs to be soft-spoken', '2025-10-26'),
(6, 11, 'caregiver for elderly', 'Looking for someone experienced in moving patients', '2025-10-27'), 
(7, 14, 'playmate for children', 'Needs help with homeworks, energy is a plus.', '2025-10-28'),
(8, 15, 'babysitter', 'Part-time sitter needed for morning hours.', '2025-11-01'),
(9, 16, 'caregiver for elderly', 'Seeking someone reliable for weekend shifts.', '2025-11-03'),
(10, 17, 'babysitter', 'Must have experience with newborns, require soft-spoken communication.', '2025-11-05'),
(11, 18, 'playmate for children', 'Looking for someone experienced with lots of energy', '2025-11-08'),
(12, 19, 'babysitter', 'Emergency evening babysitting.', '2025-11-10'),
(13, 20, 'babysitter', 'Need babysitter with flexible schedule', '2025-11-12');

INSERT INTO JOB_APPLICATION (caregiver_user_id, job_id, date_applied) VALUES
(1, 1, '2025-10-22'),
(2, 1, '2025-10-23'),
(5, 1, '2025-10-24'),
(3, 4, '2025-10-26'),
(7, 4, '2025-10-27'),
(4, 2, '2025-10-24'),
(6, 3, '2025-11-29'),
(8, 7, '2025-10-29'),
(10, 7, '2025-10-30'),
(9, 6, '2025-10-29'),
(3, 9, '2025-11-04'),
(5, 8, '2025-11-02');

INSERT INTO APPOINTMENT (appointment_id, caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status) VALUES
(1, 2, 14, '2025-12-01', '14:00:00', 3, 'confirmed'),
(2, 3, 13, '2025-12-02', '10:00:00', 4, 'confirmed'),
(3, 5, 15, '2025-12-03', '08:00:00', 8, 'confirmed'),
(4, 9, 16, '2025-12-04', '17:00:00', 2, 'confirmed'), 
(5, 1, 20, '2025-12-05', '16:00:00', 5, 'pending'),
(6, 7, 11, '2025-12-06', '12:00:00', 6, 'declined'),
(7, 4, 19, '2025-12-07', '18:00:00', 4, 'confirmed'), 
(8, 6, 17, '2025-12-08', '09:00:00', 7, 'pending'),
(9, 10, 20, '2025-12-09', '11:00:00', 2, 'confirmed'),
(10, 8, 12, '2025-12-10', '15:00:00', 3, 'confirmed');