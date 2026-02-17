// Dumps the decompressed ASCII animation from https://www.asciimation.co.nz/
if (typeof film !== 'undefined') {
    console.log("Found 'film' variable. Processing...");
    
    var content = Array.isArray(film) ? film.join('\n') : film;
    
    var blob = new Blob([content], {type: "text/plain"});
    var url = URL.createObjectURL(blob);
    
    var a = document.createElement("a");
    a.href = url;
    a.download = "starwars.txt";
    document.body.appendChild(a);
    a.click();
    
    console.log("Download started!");
} else {
    console.error("Variable 'film' not found.");
}