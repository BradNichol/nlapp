
// Function to generate download link
function downloadCSV(csv, filename) {
    let csvFile;
    let exportLink;

    // CSV file
    csvFile = new Blob([csv], {type:'text/csv'});

    // Download link
    exportLink = document.createElement('a');

    // CSV file name
    exportLink.download = filename;

    // link to file
    exportLink.href = window.URL.createObjectURL(csvFile);

    // add link to DOM
    document.body.appendChild(exportink);

    // click link
    exportLink.click();
}

// function to create CSV data from HTML table and dowload using above function
function exportTableData(filename) {
    let csv = [];
    let container = document.querySelector('#recipe_table')
    let rows = container.querySelectorAll('tr');

    for(let i=0; i < rows.length; i++) {
        let row = [], cols = rows[i].container.querySelectorAll('td, th');

        for(let j=0; j < cols.length; j++)
            row.push(cols[j].innerText);
        
        csv.push(row.join(','));
    }

    // download file
    downloadCSV(csv.join('\n'), filename);
}
