% function of lexicon based sentimental Analysis
% Input: a path to the target text file
% Output: a sentimental score of the text

function sent_score = sentimentalAnalysis(filename)

lexicon = '../Data/wordwithStrength.txt';

[fid, msg] = fopen(lexicon, 'rt');
error(msg);
line = fgets(fid); % Get the first line from the file.
%Initialize a Map structure to store the lexicon
cM = containers.Map();
while line ~= -1

    %fprintf('%s', line); % Print the line on
    ii = 1;
    token={};
    while any(line)
        [token{ii}, line] = strtok(line);
        % Repeatedly apply the strtok function.
        ii = ii + 1; 
    end
    cM(token{1}) = str2double(token{2});
    
    line = fgets(fid); % Get the next line from the file.
    
end
fclose(fid);


[fid, msg] = fopen(filename, 'rt');
error(msg);
line = lower(fgets(fid)); % Get the first line from the file.

test_token={};
ii = 1;
while line ~= -1
     %Store each word in the test_token array
     while any(line)
         %PUT YOUR IMPLEMENTATION HERE
         [test_token{ii}, line] = strtok(line, ' ,.:;[](){}<>*^&%$#@!?''"');
         ii = ii + 1;
     end
     
     line = lower(fgets(fid));
end
fclose(fid);

sent_score = 0;
total = 0;
num_considered = 0;
key_exists = isKey(cM, test_token);
for k=1:length(test_token)
    %PUT YOUR IMPLEMENTATION HERE
    if key_exists[k]
        total = total+cM(test_token{k});
        num_considered = num_considered + 1;
    end
end 

sent_score = total / num_considered;

if sent_score > 0
     if sent_score > 0.7
         disp(sent_score);
         disp('Highly Positive Sentiment');
     else
        disp(sent_score);
        disp('Positive Sentiment');
     end
end

if sent_score < 0
    if sent_score < -0.7
         disp(sent_score);
         disp('Highly Negative Sentiment');
    else
         disp(sent_score);
         disp('Negative Sentiment');
    end
end

if sent_score == 0
    disp('Neutral Sentiment');
end
