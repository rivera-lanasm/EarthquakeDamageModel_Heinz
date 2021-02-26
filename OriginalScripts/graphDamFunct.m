function [Pslight,Pmoderate,Pextensive,Pcomplete] = graphDamFunct(bldgType, PGA, DFV, rowNum)
% Madeline Jones 4/17/218
%   Earthquake Damage Assessment Model

%% Get  Median and Beta variables
%Median
MedianSlight=DFV(rowNum,1);
MedianModerate=DFV(rowNum,2);
MedianExtensive=DFV(rowNum,3);
MedianComplete=DFV(rowNum,4);
%Beta
Bslight=0.64;
Bmoderate=0.64;
Bextensive=0.64;
Bcomplete=0.64;

%%  Fragility Functions
%Define dx and dy, max x
x=0:0.1:4; %PGA
y=0:0.1:1; %Probability of reaching or exceeding a certain damage state

slight=normcdf((1/Bslight)*log(x/MedianSlight));
moderate=normcdf((1/Bmoderate)*log(x/MedianModerate));
extensive=normcdf((1/Bextensive)*log(x/MedianExtensive));
complete=normcdf((1/Bcomplete)*log(x/MedianComplete));

% %% Plot Figure
% figure(1);
% plot(x,slight);
% hold on; 
% plot(x,moderate);
% hold on;plot(x,extensive);
% hold on;plot(x,complete);
% hold on; plot([PGA PGA],[0 1],'k--')



title(bldgType)
ylabel('Probability of Reaching and Exceeding Damage State')
xlabel('PGA')
legend('slight','moderate','extensive','complete','PGA')


%% Get Damage

Pslight = normcdf((1/Bslight)*log(PGA/MedianSlight));
Pmoderate = normcdf((1/Bmoderate)*log(PGA/MedianModerate));
Pextensive = normcdf((1/Bextensive)*log(PGA/MedianExtensive));
Pcomplete = normcdf((1/Bcomplete)*log(PGA/MedianComplete));

end

