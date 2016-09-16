% function to create a vocabulary from multiple text files under folders

function feat_vec = cse408_bow(filepath, voc)

[fid, msg] = fopen(filepath, 'rt');
error(msg);
line = fgets(fid); % Get the first line from
 % the file.
feat_vec = zeros(size(voc)); %Initialize the feature vector'
while line ~= -1

    %PUT YOUR IMPLEMENTATION HERE
    %While the current line isn't empty
    while isempty(line) == 0
        % Get token from array
        [Token, line] = strtok(line);
        %Make token into only lower case
        %letter word (without punctuation)
        Word = lower(Token);
        Indexes = regexp(Word, '[a-z]');
        Word = Word(Indexes);
        %Get Index of Word in voc
        index = strcmp(Word,voc);
        %Increment Feature Vector Based on Index of
        %Voc Word
        feat_vec(index) = feat_vec(index) + 1;
    end
    %Get next line of the file
    line = fgets(fid);
end
fclose(fid);