% Function goes to a file path and loops through
% all of the images in the folder in order to create
% a feature library of the images

function featLibrary = createFeatureLibrary(filePath)

images = dir(fullfile(filePath,'*.png'));
featLibrary = {};

for img = images'
    fullImagePath = fullfile(filePath,img.name);
    display(fullImagePath);
    featLibrary = [featLibrary {featureExtraction(fullImagePath)}];
end