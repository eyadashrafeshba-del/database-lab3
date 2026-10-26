USE libraryDB;

INSERT INTO Author(`name`,country)
VALUES('Ezz Gamal','Egypt'),
('Ahmed Ali','UAE'),
('Mike Tyson','USA');

INSERT INTO Book(title,price,author_id)
VALUES('SOFTWARE IN BRIEF',125.22,1),
('How to become rich in 60 Days',67.99,2),
('Boxing Life',150.57,3),
('ADVANCED SOFTWARE OOD',299.70,1),
('My Life in France',60.99,2),
('MMA Fighter Story',99.99,3);
