CREATE TABLE IF NOT EXISTS image (
    id SERIAL PRIMARY KEY,
    path varchar(256)
);


CREATE TABLE IF NOT EXISTS label (
    id SERIAL PRIMARY KEY,
    image_id INT,
    x INT CHECK (x >= 0 AND x < 65536),
    y INT CHECK (y >= 0 AND y < 65536),
    width INT CHECK (width >= 0 AND width < 65536 AND x + width < 65536),
    height INT CHECK (height >= 0 AND height < 65536 AND y + height < 65536),
    misc JSON,
    FOREIGN KEY (image_id) REFERENCES image(id)
);