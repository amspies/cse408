%Returns a feature vector of extracted features from image
%Index 1: File Path Name
%Index 2: Average Pixel Color (Not including rgb(0,0,0))
%Index 3: Spatial Grid of Average Pixel Color
%Index 4: Color Histogram

function featVect = featureExtraction(imageFileName)
    % Read in an image and convert it to RGB
    [I,C] = imread(imageFileName);
    if ~isempty(C)
        rgbImage = ind2rgb(I,C);
    end
    %image(rgbImage);
    % Average Pixel Color
    % Since PNG is put in MATLAB with all black background
    % we are going to not have anything in average if it is
    % pure black (0,0,0) so the average for the image is not
    % skewed
    re = rgbImage(:,:,1);
    gr = rgbImage(:,:,2);
    bl = rgbImage(:,:,3);
    count = 0;
    reTotal = 0;
    grTotal = 0;
    blTotal = 0;
    for i = 1:numel(re)
        if re(i) == 0 && gr(i) == 0 && bl(i) == 0
            %DO NOTHING FOR ALL BLACK
        else
            count = count + 1;
            reTotal = reTotal + re(i);
            grTotal = grTotal + gr(i);
            blTotal = blTotal + bl(i);
        end
    end
    rgbPixelAverage = [reTotal,grTotal,blTotal] ./ count;
    
    % Spatial Grid of average pixel color
    % All pictures are made into an 8x8 grid
    % of the average colors that were around
    % the pixel. These RGB values were then
    % stored in a vector that will be put into
    % the feature cell vector.
    spa = [];
    reSpatial = re;
    grSpatial = gr;
    blSpatial = bl;
    for j = 0:7
        start = ((j)*16)+1;
        stop = ((j+1)*16);
        for i = 0:7
           innerStart = ((i)*16)+1;
           innerStop = ((i+1)*16);
           redMean = mean2(reSpatial(start:stop,innerStart:innerStop));
           reSpatial(start:stop,innerStart:innerStop) = redMean;
           greenMean = mean2(grSpatial(start:stop,innerStart:innerStop));
           grSpatial(start:stop,innerStart:innerStop) = greenMean;
           blueMean = mean2(blSpatial(start:stop,innerStart:innerStop));
           blSpatial(start:stop,innerStart:innerStop) = blueMean;
           spa = [spa,redMean,greenMean,blueMean];
        end
    end
    
    %testImage = cat(3,reSpatial,grSpatial,blSpatial);
    %imshow(testImage);
    
    % Color Histogram
    % Concatenated Red, Green, and Blue Color Histograms
    % of the image.
    redHist = hist(reshape(double(rgbImage(:,:,1)),[128*128 1]),25);
    greenHist = hist(reshape(double(rgbImage(:,:,2)),[128*128 1]),25);
    blueHist = hist(reshape(double(rgbImage(:,:,3)),[128*128 1]),25);
    completeHist = [redHist, greenHist, blueHist];
    
    featVect = {imageFileName,rgbPixelAverage,spa,completeHist};
end