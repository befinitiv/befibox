$fn=64;

D = 5;
B = 25;



cylinder(d=B+D, h=2);
/*linear_extrude(3)minkowski() {
    circle(d=D);
    square([B,B], center=true);
}*/

H = B;
translate([0,0,H/2])cube([B+D, 2, H], center=true);
translate([0,0,H])rotate([90,0,0])cylinder(d=B+D, h=2, center=true);