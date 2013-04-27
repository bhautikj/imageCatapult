-- Reference:
-- Using sqlite
-- Available types: NULL (None), INTEGER, REAL (float), TEXT (string), DATE

create table tag (
  tagId             integer primary key autoincrement not null,
  tag               text
);

create table image (
  imageId           integer primary key autoincrement not null,
  copyrightNotice   text,
  author            text,
  title             text,
  dburl             text,
  description       text,
  tags              text,
  width             integer,
  height            integer,
  imagesize         integer,
  unixTime          integer,
  geoCode           integer,
  latitude          integer,
  longitude         integer
);

create table flickrImage (
  imageId           integer REFERENCES image(imageId),
  flickrSets        text,
  flickrGroups      text,
  url               text,
  shorturl          text,
  photoId           text,
  imageThumbUrl     text,
  imageLargeUrl     text
);

create table template (
  templateId        integer primary key autoincrement not null,
  name              text,
  dict              text
);

create table flickrGroups (
  nsid              text primary key not null,
  name              text
);

create table flickrSets (
  id                text primary key not null,
  name              text
);

create table job (
  jobId             integer primary key autoincrement not null, 
  imageId           integer REFERENCES image(imageId),
  jobTime           integer,
  jobDict           text,
  status            text
);