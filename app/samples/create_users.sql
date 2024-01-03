-- Insert the first user (STUDENT)
INSERT INTO user (type, email, stake_address, active, email_validation_string, register_date)
VALUES ('student', 'student1@email.com', 'stake_test123', true, 'random_string', DATE('now'));

INSERT INTO user (type, email, stake_address, active, email_validation_string, register_date)
VALUES ('student', 'student2@email.com', 'stake_test456', true, 'random_string', DATE('now'));

-- Insert the third user (ORGANIZER)
INSERT INTO user (type, email, stake_address, active, email_validation_string, register_date)
VALUES ('organizer', 'organizer1@email.com', 'stake_test789', true, 'random_string', DATE('now'));

-- Insert the second user (TEACHER)
INSERT INTO user (type, email, stake_address, active, email_validation_string, register_date)
VALUES ('teacher', 'teacher1@email.com', 'stake_testabc', true, 'random_string', DATE('now'));
