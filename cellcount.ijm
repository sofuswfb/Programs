// Specify the folder containing the TIF files
inputDir = getDirectory("Choose a Directory");

// Get a list of all TIF files in the folder
list = getFileList(inputDir);

// Create arrays to store the results
numFiles = list.length;
names = newArray(numFiles);

// Initialize variables for storing all results
summaryResults = "File,Average Area,Average Circularity,Particle Count\n";

firstFileName = "";
firstFileBaseName = "";

for (i = 0; i < numFiles; i++) {
    if (endsWith(list[i], ".tif") || endsWith(list[i], ".TIF")) {
        if (firstFileName == "") {
            firstFileName = list[i];
            firstFileBaseName = substring(firstFileName, 0, indexOf(firstFileName, "."));
        }

        // Open the image
        open(inputDir + list[i]);

        // Convert the image to 8-bit
        run("8-bit");

        // Apply the threshold using the "Triangle" method with Black Background
        setAutoThreshold("Triangle dark");
        setOption("BlackBackground", true);
        run("Convert to Mask");

        // Apply a median filter with a radius of 2
        run("Median...", "radius=2");

        // Apply watershed
        run("Watershed");

        // Clear the previous results
        run("Clear Results");

        // Analyze particles with specified parameters and store results
        run("Analyze Particles...", "size=20-100 circularity=0.00-1.00 show=Overlay display add");

        // Store the results
        counts = nResults;
        totalArea = 0;
        totalCircularity = 0;

        // Prepare the individual file results
        individualResults = "X,Y,Area,Circularity\n";
        
        for (j = 0; j < counts; j++) {
            x = getResult("X", j);
            y = getResult("Y", j);
            area = getResult("Area", j);
            circularity = getResult("Circ.", j);
            individualResults += x + "," + y + "," + area + "," + circularity + "\n";
            totalArea += area;
            totalCircularity += circularity;
        }

        // Calculate averages
        if (counts > 0) {
            averageArea = totalArea / counts;
            averageCircularity = totalCircularity / counts;
        } else {
            averageArea = 0;
            averageCircularity = 0;
        }

        // Append to summary results
        summaryResults += list[i] + "," + averageArea + "," + averageCircularity + "," + counts + "\n";

        // Save the individual results to a CSV file
        individualFileName = substring(list[i], 0, indexOf(list[i], ".")) + "_results.csv";
        individualOutputFile = inputDir + individualFileName;
        File.saveString(individualResults, individualOutputFile);

        // Add overlay with red outlines
        run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction stack display redirect=None decimal=3");
        roiManager("Show None");
        run("Outline", "color=red");
        saveAs("Tiff", inputDir + substring(list[i], 0, indexOf(list[i], ".")) + "_overlay.tif");

        // Close the image
        close();
    }
}

// Save the summary results to a CSV file in the same folder as the TIF files
summaryOutputFile = inputDir + firstFileBaseName + "_summary_results.csv";
File.saveString(summaryResults, summaryOutputFile);

print("Results saved to: " + summaryOutputFile);
