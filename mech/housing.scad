$fn=64;


GLASS_XY = 100;
//we need to widen the housing to find space where there will be no reflections from the LEDs
EXTRA_XY = GLASS_XY/2+20;
GLASS_Z = 3;

WALL_TH = 3;

//CAM_TO_GLASS_Z = 165; //PI 2 camera
CAM_TO_GLASS_Z = 140;

CORNER_RADIUS = 5;


Z_BASE = WALL_TH + CAM_TO_GLASS_Z + GLASS_Z - 30;

Z_CAP = WALL_TH+CAM_TO_GLASS_Z+2*GLASS_Z-Z_BASE;

CAP_LID_Z = 10;
CAP_LID_TH = 2;

CAM_X = 20;
CAM_Y = 20;


SPEAKER_MOUNT_H = 30;

SPEAKER_X = 90;
SPEAKER_Y = 50;

//height is also the circle diameter
SPEAKER_BASE_FORM_D = 43;
//width
SPEAKER_BASE_FORM_X = 83;


module speaker_base_form() {
    translate([(SPEAKER_BASE_FORM_X-SPEAKER_BASE_FORM_D) / 2,0,0])circle(d=SPEAKER_BASE_FORM_D);
    
    square([SPEAKER_BASE_FORM_X-SPEAKER_BASE_FORM_D, SPEAKER_BASE_FORM_D], center=true);
    translate([-(SPEAKER_BASE_FORM_X-SPEAKER_BASE_FORM_D) / 2,0,0])circle(d=SPEAKER_BASE_FORM_D);
    
}

module speaker_drill_pattern(){
    for(x = [1, -1])
        for(y = [1, -1])
            translate([x*74/2, y*39/2, 0])children();
}

module speaker_mount() {
    difference() {
        union() {
        linear_extrude(2)difference() {
            square([SPEAKER_X, SPEAKER_Y], center=true);
            speaker_base_form();
        }
        speaker_drill_pattern()cylinder(d=6, h=2+2);
    }
    speaker_drill_pattern()cylinder(d=3, h=100);
}
}

module speaker_grill() {
    
    HOLE_XY = 3;
    HOLE_SPACING = 6;
    intersection() {
        linear_extrude(WALL_TH*4)speaker_base_form();
        
        for(x = [-SPEAKER_X/HOLE_SPACING:1:SPEAKER_X/HOLE_SPACING]) {
            for(y = [-SPEAKER_Y/HOLE_SPACING:1:SPEAKER_Y/HOLE_SPACING]) {
                translate([x*HOLE_SPACING,y*HOLE_SPACING, 0])cube([HOLE_XY, HOLE_XY, 100], center=true);
            }
        }
    }
}


//TODO
// RPI-Halter
// Wlanhalter

//Reflexionen checken!

module base_form_inner() {
    minkowski() {
        square([GLASS_XY+EXTRA_XY-CORNER_RADIUS*2, GLASS_XY+EXTRA_XY-CORNER_RADIUS*2], center=true);
        circle(r=CORNER_RADIUS);
    }
}




module camera_mount() {
    TH = 2;
    Z = 20;
    difference() {
        translate([0,0,Z/2])cube([CAM_X+2*TH, CAM_Y+2*TH, Z], center=true);
        
        translate([0,0,100/2+2])cube([CAM_X+0.8, CAM_Y+0.8, 100], center=true);
        cube([CAM_X-1, CAM_Y-1, 100], center=true);
        
        CABLE_Y = 15;
        translate([100/2, 0, 0])cube([100, CABLE_Y+0.5, 100], center=true);
    }
}




module led_mount() {
    LED_D = 5;
    ANGLE = 50;
    LED_MOUNT_L = 15;
    
    difference() {
        rotate([ANGLE,0,0])difference() {
            cylinder(d=LED_D+2*2, h=LED_MOUNT_L*2, center=true);
            cylinder(d=LED_D+0.5, h=100, center=true);
            
            translate([0,0,LED_MOUNT_L/5])rotate([0,-90, 90])cylinder(d=5, h=100);
        }
        
        translate([0,50,0])cube([100, 100, 100], center=true);
    }
}

module housing() {
    
    difference() {
        linear_extrude(Z_BASE)scale([(GLASS_XY+2*WALL_TH)/GLASS_XY,(GLASS_XY+2*WALL_TH)/GLASS_XY,1])base_form_inner();
        
        translate([0,0,WALL_TH])linear_extrude(Z_BASE*2)base_form_inner();
        
        translate([0,-(GLASS_XY+EXTRA_XY)/2,SPEAKER_MOUNT_H])rotate([90,0,0])speaker_grill();
        
        
    //hole for power cable
    D_CABLE_HOLE = 8;
    translate([(GLASS_XY+EXTRA_XY)/2-D_CABLE_HOLE/2+-CORNER_RADIUS,(GLASS_XY+EXTRA_XY)/2,D_CABLE_HOLE/2+WALL_TH])rotate([-90,0,0])cylinder(d=D_CABLE_HOLE, h=100, center=true);
    
        //marker for center of housing
        translate([0,0,WALL_TH-1])cylinder(h=1, d=3);
        }
    
    translate([0,-(GLASS_XY+EXTRA_XY)/2,SPEAKER_MOUNT_H])rotate([-90,0,0])speaker_mount();

    
    
    for(i = [0:3])rotate([0,0,90*i])translate([0,(GLASS_XY+EXTRA_XY)/2,CAM_TO_GLASS_Z-42])led_mount();
        
/*
    translate([0,0,WALL_TH-0.1])camera_mount();
    
    //RPI holder
    RPI_HOLDER_Z = 50;
    translate([(GLASS_XY+EXTRA_XY)/2+2,0,RPI_HOLDER_Z/2])rotate([0,0,90])generic_holder(50, 10, RPI_HOLDER_Z);
    
    WIFI_HOLDER_Z = 50;
    //wifi holder
    translate([0, (GLASS_XY+EXTRA_XY)/2+2,WIFI_HOLDER_Z/2])rotate([0,0,180])generic_holder(50, 10, WIFI_HOLDER_Z);
    */
    
    translate([((GLASS_XY+EXTRA_XY)/2-60)/2-(GLASS_XY+EXTRA_XY)/2,0,60/2+WALL_TH])cube([(GLASS_XY+EXTRA_XY)/2-60, 20, 60], center=true);
}

module cap() {
difference() {
        linear_extrude(Z_CAP)scale([(GLASS_XY+2*WALL_TH)/GLASS_XY,(GLASS_XY+2*WALL_TH)/GLASS_XY,1])base_form_inner();
        
        scale([(GLASS_XY+EXTRA_XY-2*0.5)/(GLASS_XY+EXTRA_XY),(GLASS_XY+EXTRA_XY-2*0.5)/(GLASS_XY+EXTRA_XY),1])translate([0,0,-Z_CAP-2*GLASS_Z])linear_extrude(Z_CAP*2)base_form_inner();
    
        translate([0,0,GLASS_Z+Z_CAP-GLASS_Z])cube([GLASS_XY+0.8, GLASS_XY+0.8, GLASS_Z*2], center=true);
    
        cube([GLASS_XY-2, GLASS_XY-2, 100], center=true);
}

difference() {
scale([(GLASS_XY+EXTRA_XY-2*0.5)/(GLASS_XY+EXTRA_XY),(GLASS_XY+EXTRA_XY-2*0.5)/(GLASS_XY+EXTRA_XY),1])translate([0,0,-CAP_LID_Z])linear_extrude(CAP_LID_Z+Z_CAP)base_form_inner();
    
    translate([0,0,-50])linear_extrude(100)scale([(GLASS_XY+EXTRA_XY-2*CAP_LID_TH)/(GLASS_XY+EXTRA_XY),(GLASS_XY+EXTRA_XY-2*CAP_LID_TH)/(GLASS_XY+EXTRA_XY),1])base_form_inner();
}

for(i=[0:3])rotate([0,0,90*i])translate([(GLASS_XY+EXTRA_XY)/2-1,0,-CAP_LID_Z+3])sphere(d=2.5);
    
for(i=[0:3])rotate([0,0,90*i])translate([GLASS_XY/2+1,0,Z_CAP-2])sphere(d=2);

}


module generic_holder(x_inner, y_inner, z) {
    TH = 2;
    translate([0,y_inner/2+TH,0])difference() {
        cube([x_inner+2*TH, y_inner+2*TH, z], center=true);
        cube([x_inner, y_inner, z*3], center=true);
       
        translate([0, y_inner/2, 0])cube([x_inner/1.5, y_inner, z*3], center=true);
   }
}


//color("red")rotate([90,0,0])polygon([[0,0], [GLASS_XY/2, CAM_TO_GLASS_Z], [GLASS_XY, 0]]);


difference() {
    union() {
housing();

//translate([0,0,Z_BASE])cap();
    }
        cube([1000,1000,1000]);
}