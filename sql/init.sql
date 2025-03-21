-- Création de la table si elle n'existe pas
CREATE TABLE IF NOT EXISTS tweets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    positive BOOLEAN NOT NULL,
    negative BOOLEAN NOT NULL
);

-- Insertion des données d'exemple
INSERT INTO tweets (text, positive, negative) VALUES 
('I love this product, it''s amazing!', 1, 0),
('This is the worst experience ever', 0, 1),
('Great customer service, very helpful', 1, 0),
('Terrible quality, do not recommend', 0, 1),
('The food was delicious', 1, 0),
('Very disappointed with the service', 0, 1),
('Awesome experience, will come back', 1, 0),
('This is a complete waste of money', 0, 1),
('Really happy with my purchase', 1, 0),
('Poor quality and bad service', 0, 1),
('The interface is so user-friendly', 1, 0),
('Buggy software, crashes all the time', 0, 1),
('Best purchase I''ve made this year', 1, 0),
('Shipping was too slow', 0, 1),
('Amazing features and performance', 1, 0),
('Customer support never responded', 0, 1),
('Works perfectly, highly recommend', 1, 0),
('Waste of time and money', 0, 1),
('Super fast delivery and great packaging', 1, 0),
('Product broke after one week', 0, 1),
('Excellent value for money', 1, 0),
('Very poor build quality', 0, 1),
('The team was very professional', 1, 0),
('Horrible experience overall', 0, 1),
('Everything works as advertised', 1, 0); 