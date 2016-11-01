%Returns a feature vector of extracted features from image
%Index 1: File Path Name
%Index 2: Average Pixel Color (Not including rgb(0,0,0))
%Index 3: Spatial Grid of Average Pixel Color
%Index 4: Color Histogram
%Index 5: Edge Dectection using Image Segmentation 

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
    reTotal = mean2(re);
    grTotal = mean2(gr);
    blTotal = mean2(bl);
    rgbPixelAverage = [reTotal,grTotal,blTotal];
    
    % Spatial Grid of average pixel color
    % All pictures are made into an 8x8 grid
    % of the average colors that were around
    % the pixel. These RGB values were then
    % stored in a vector that will be put into
    % the feature cell vector.
    %Pixel Width of Squares
    PIXEL_WIDTH = 16;
    NUM_SQS = (128/PIXEL_WIDTH)- 1;
    spa = [];
    reSpatial = re;
    grSpatial = gr;
    blSpatial = bl;
    for j = 0:NUM_SQS
        start = ((j)*PIXEL_WIDTH)+1;
        stop = ((j+1)*PIXEL_WIDTH);
        for i = 0:NUM_SQS
           innerStart = ((i)*PIXEL_WIDTH)+1;
           innerStop = ((i+1)*PIXEL_WIDTH);
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
    
    %Edge Dectection using Image Segmentation
    %Edge Detection Part
    [~, threshold] = edge(I, 'sobel');
    fudgeFactor = 0.5;
    BWs = edge(I, 'sobel', threshold * fudgeFactor);
    se90 = strel('line', 3, 90);
    se0 = strel('line', 3, 0);
    BWsdil = imdilate(BWs, [se90, se0]);
    BWdfill = imfill(BWsdil, 'holes');
    BWnobord = imclearborder(BWdfill, 4);
    seD = strel('diamond', 1);
    BWfinal = imerode(BWnobord, seD);
    BWfinal = imerode(BWfinal, seD);
    %Image Segmentation Part
    BWspatial = [];
    %Pixel Width of squares
    PIXEL_WIDTH = 8;
    NUM_SQS = (128/PIXEL_WIDTH)- 1;
    bwCopy = BWfinal;
    for j = 0:NUM_SQS
        start = ((j)*PIXEL_WIDTH)+1;
        stop = ((j+1)*PIXEL_WIDTH);
        for i = 0:NUM_SQS
           innerStart = ((i)*PIXEL_WIDTH)+1;
           innerStop = ((i+1)*PIXEL_WIDTH);
           bwMean = mean2(bwCopy(start:stop,innerStart:innerStop));
           bwCopy(start:stop,innerStart:innerStop) = bwMean;
           BWspatial = [BWspatial,bwMean];
        end
    end
    
    %imshow(bwCopy);
    
    featVect = {imageFileName,rgbPixelAverage,spa,completeHist, BWspatial};
end