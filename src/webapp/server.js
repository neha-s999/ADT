var express = require("express");
var fs = require("fs");
var axios = require("axios");
var multer = require("multer");
var upload = multer({ dest: "uploads/" });
var app = express();
const path = require("path");

app.set("views", path.join(__dirname, "views"));

// Set the view engine to ejs
app.set("view engine", "ejs");
app.use("/public", express.static(__dirname + "/public"));

// Index page
app.get("/", function (req, res) {
  res.render("pages/index");
});

app.get("/sample", function (req, res) {
  res.json({ mil: "teste" });
});

app.post("/submit-image", upload.single("file"), function (req, res, next) {
  console.log(req.file, "check this");
  // Assuming uploads folder is two levels up from the webapp directory
  const uploadsFolderPath = path.join(__dirname, "../../uploads/");
  console.log("Upload Folders Path: ", uploadsFolderPath)
  var suggestions_url = "http://127.0.0.1:5000/path";
  axios
    .post(suggestions_url, {
      filepath: path.join(uploadsFolderPath, req.file.filename),
      // filepath: __dirname + "/" + req.file.path,\
    })
    .then(function (response) {
      res.json(response.data);
    })
    .catch(function (error) {
      // console.error(error);
      res.status(500).send("Internal Server Error");
    });
});

app.post("/descriptor", function (req, res) {
  var description_url = "http://127.0.0.1:5001";

  var product_name = req.query.product_name;

  axios
    .post(description_url, {
      product_name: product_name,
    })
    .then(function (response) {
      console.log(response.data);
      res.json(response.data);
    })
    .catch(function (error) {
      console.error(error);
      res.status(500).send("Internal Server Error");
    });
});
app.get("/descriptor", function (req, res) { // Change to GET
  var description_url = "http://127.0.0.1:5001/descriptor";
  
  var product_name = req.query.product_name;

  axios
    .get(description_url, { // Change to GET
      params: {
        product_name: product_name,
      },
    })
    .then(function (response) {
      console.log(response.data);
      res.json(response.data);
    })
    .catch(function (error) {
      console.error(error);
      res.status(500).send("Internal Server Error");
    });
});


app.get("/suggestions", function (req, res) {
  var calories = req.query.calories;
  var cholesterol = req.query.cholesterol;
  var carbohydrates = req.query.carbohydrates;
  var fat = req.query.fat;
  var fiber = req.query.fiber;
  var proteins = req.query.proteins;

  var suggestions_url = "http://127.0.0.1:5002";

  axios
    .post(suggestions_url, {
      calories: calories,
      cholesterol: cholesterol,
      carbohydrates: carbohydrates,
      fat: fat,
      fiber: fiber,
      proteins: proteins,
    })
    .then(function (response) {
      res.json(response.data);
    })
    .catch(function (error) {
      console.error(error);
      res.status(500).send("Internal Server Error");
    });
});

app.listen(8080);
console.log("8080 is the magic port");
