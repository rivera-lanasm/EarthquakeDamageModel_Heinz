%% Define Building Type and Variables
BldgType='W1 High-Code';

%Beta
Bslight=0.64;
Bmoderate=0.64;
Bextensive=0.64;
Bcomplete=0.64;
%Median
PGAslight=0.26;
PGAmoderate=0.55;
PGAextensive=1.28;
PGAcomplete=2.01;


%addpath('C:\Users\Madeline Jones\Documents\ArcGIS\PtolemyEarthquake')

%% Fragility Functions

%Define dx and dy, max x
x=0:0.1:4; %PGA
y=0:0.1:1; %Probability of reaching or exceeding a certain damage state

slight=normcdf((1/Bslight)*log(x/PGAslight));
moderate=normcdf((1/Bmoderate)*log(x/PGAmoderate));
extensive=normcdf((1/Bextensive)*log(x/PGAextensive));
complete=normcdf((1/Bcomplete)*log(x/PGAcomplete));


%% Plot Figure

figure(1);plot(x,slight);hold on; plot(x,moderate);hold on;plot(x,extensive);hold on;plot(x,complete)
figure(1); title('Probability of Reaching and Exceeding Various Damage States for: W1 Special High-Code')

ylabel('Probability of Reaching and Exceeding Damage State')
xlabel('PGA')
legend('slight','moderate','extensive','complete')