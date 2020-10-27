const express = require("express");
const cors = require('cors')
const app = express();
let extractedGrid = "";

app.use(express.urlencoded());
app.use(express.json())
app.use(cors({ origin: true, credentials: true }));

app.post("/extract", async(req, res) => {
    console.log("entrou no extract")
    const { spawn } = require("child_process");
    let pathImage = req.body.path;
    const pyProg = await spawn("python", ["./elements_board_extractor.py", "--pathImage=" + pathImage]);
    let aux = [];
    pyProg.stdout.on('data', function(data) {
        console.log("dsstaaaaa------")
        console.log(data.toString());
        console.log("depois do data");
        extractedGrid = data.toString();
        extractedGrid = extractedGrid.split("");
        let line = "";
        console.log(extractedGrid)
        let finalGrid = [];
        extractedGrid.forEach((e, i) => {
            if (e == "\n" && extractedGrid[i + 1]) {
                line += ",";

            } else if (e != "\n" && e != "\r") {
                line += e + " ";
            }
        })
        console.log("##final-grid")
        console.log(line)
        res.json({ board: line });
    });
})

app.post("/resolve", async(req, res) => {
    const { spawn } = require("child_process");
    let board = req.body.board;
    console.log("board da req")
    console.log(board);
    const pyProg = await spawn("python", ["./sudoku_genetic_python.py", board]);
    let resolution = "";
    pyProg.stdout.on('data', function(data) {
        resolution = data.toString();
        res.json({ resolution });
    });
})

app.get("/ping", (req, res) => {
    res.json({ msg: "teste ping ok" });
})
app.listen(4000, () => {
    console.log(("teste listening"))
})