D = 5;
B = 25;


linear_extrude(3)minkowski() {
    circle(d=D);
    square([B,B], center=true);
}

translate([0,0,2*B/2])cube([B+D, 3, 2*B], center=true);
translate([0,0,2*B])rotate([90,0,0])cylinder(d=B+D, h=3, center=true);