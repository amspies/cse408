answer = '0';

library = createFeatureLibrary('../Data/Database');

while answer ~= '2'
    answer = input('\nWhat do you want to do?\n1)Query for Image\n2)Quit\nChoice: ','s');
    if answer == '1'
        featureChoice = input('\nWhat feature do you want to use?\n1)Average Pixel Color\n2)Spatial Grid of Average Pixel Color\n3)Color Histograms\n4)Edge Dectection using Spatial Grid\nAnswer: ');
        featureChoice = featureChoice + 1;
        algoChoice = input('\nWhich distance algorithm do you want to use?\n1)SSD\n2)Angle Between Vectors\nChoice: ');
        if (algoChoice == 1 || algoChoice == 2) && (featureChoice > 1 && featureChoice < 6)
            fileNameForFeatureVect = input('\nEnter filename (of image in /Data/Database)\n of image you want to retrieve\n top 10 matches from: ','s');
            fullImagePath = fullfile('../Data/Database',fileNameForFeatureVect);
            testVect = featureExtraction(fullImagePath);
            distance = distanceVect(algoChoice,featureChoice, library, testVect);
            [B,I] = sort(distance);
            for i=1:10
                [J,C] = imread(library{I(i)}{1});
                J = imresize(J, [128 128]);
                if ~isempty(C)
                    rgbImage = ind2rgb(J,C);
                else
                    rgbImage = im2double(J);
                end
                if i == 1
                    currentImage = rgbImage;
                else
                    currentImage = cat(2,currentImage,rgbImage);
                end
            end
            figure,imshow(currentImage);
        else
            display('Invalid Choices, Try Again.')
        end
    elseif answer ~= '2'
        display('Invalid Choice, Try Again.');
    end
end


