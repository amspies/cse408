% function to create a vocabulary from multiple text files under folders

function voc = buildVoc(folder, voc)

stopword = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', ...
    'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', ...
    'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', ...
    'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', ...
    'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', ...
    'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', ...
    'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', ...
    'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', ...
    'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', ...
    'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', ...
    'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', ...
    'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', ...
    'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', ...
    'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', ...
    'further', 'was', 'here', 'than'}; % define English stop words, from NLTK



files = dir(fullfile(folder,'*.txt'));
voc = {};

for file = files'
    [fid, msg] = fopen(fullfile(folder,file.name), 'rt');
    disp(file.name);
    error(msg);
    line = fgets(fid); % Get the first line from
     % the file.
    while line ~= -1
        %PUT YOUR IMPLEMENTATION HERE
        % While the current line isn't empty
        while isempty(line) == false
            %Get the next word in the line
            [token, line] = strtok(line);
            %Make the word lower case
            word = lower(token);
            %Get indexes of all lower case letters in string
            properCharIndexes = regexp(word, '[a-z]');
            %Remove all non lower case letters (basically punctuation from
            %string
            word = word(properCharIndexes);
            %If word is not a stop word and is not the empty string, 
            %add it to the vocabulary.
            if ismember(word, stopword)
                %disp(word);
            elseif isempty(word) == false
                voc = [voc {word}];
            end
        end
        %Once line is read through, get next line in the file.
        line = fgets(fid);
    end
    %Finally, make every word in the cell array Unique
    voc = unique(voc);
    fclose(fid);
end
