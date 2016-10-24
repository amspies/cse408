answer = '0';

while answer ~= '2'
    answer = input('What do you want to do?\n1)Query for Image\n2)Quit\nChoice: ','s');
    if answer == '1'
        testFunction(1)
    elseif answer ~= '2'
        display('Invalid Choice, Try Again.');
    end
end

function [n] = testFunction(a)
    display(a);
    n = a;
end

