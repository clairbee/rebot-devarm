# arm

reBot Arm B601 DM (structure only so far - see PARTCAD.md)

Package: `//pub/robotics/rebot/devarm/b601-dm`

<img src="./doc/arm.svg" alt="arm" style="width: auto; height: auto; max-width: 200px; max-height: 200px;">

## Sub-Assemblies

### [//pub/robotics/rebot/devarm/b601-dm](README.md)

| Assembly |  | Count | File | Description |
| --- | --- | ---: | --- | --- |
| gripper | <img src="./doc/gripper.svg" alt="gripper" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | `gripper.assy` | The B601 DM gripper as the released assembly holds it (49 components) |

## Parts

### [//pub/robotics/rebot/devarm/b601-dm](README.md)

| Part |  | Count | Material | Method | Process | Tolerance | Vendor | SKU | File | Description |
| --- | --- | ---: | --- | --- | --- | ---: | --- | --- | --- | --- |
| actuator-dm4310 | <img src="./doc/actuator-dm4310.svg" alt="actuator-dm4310" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 4 | aluminium alloy |  |  |  | seeedstudio | [DIP-Servo-Motor-24V-120RPM-Brushless-98-9mm-4P-L56-W56-H46mm-p-6660](https://www.seeedstudio.com/DIP-Servo-Motor-24V-120RPM-Brushless-98-9mm-4P-L56-W56-H46mm-p-6660.html) | `vendor/actuator-dm4310.step` | Brushless actuator DM4310(V4) (x4, joints 4-7) |
| actuator-dm4340p | <img src="./doc/actuator-dm4340p.svg" alt="actuator-dm4340p" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 3 | aluminium alloy |  |  |  | seeedstudio | [DM4340P-Actuator-p-6663](https://www.seeedstudio.com/DM4340P-Actuator-p-6663.html) | `vendor/actuator-dm4340p.step` | Brushless actuator DM4340P(V4) (x3, joints 1-3) |
| arm-handle | <img src="./doc/arm-handle.svg" alt="arm-handle" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Arm_Handle.step` | Arm handle (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| arm-yaw-limit | <img src="./doc/arm-yaw-limit.svg" alt="arm-yaw-limit" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Arm_Yaw_Limit.step` | Motor 1 rotation axis, yaw angle motion limit (x1) |
| base-link | <img src="./doc/base-link.svg" alt="base-link" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_BASE_Link.step` | Robotic arm base link (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| base-plate | <img src="./doc/base-plate.svg" alt="base-plate" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_BASE_Plate.step` | Robotic arm base platform (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| base-reinforcement | <img src="./doc/base-reinforcement.svg" alt="base-reinforcement" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Base_Reinforcement_Part.step` | Motor 1 bearing mount (x1) - can be printed in ABS at high infill to save cost |
| bearing-6707zz | <img src="./doc/bearing-6707zz.svg" alt="bearing-6707zz" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | chrome steel (AISI 52100) |  |  |  | amazon | B0D6WBMW3F | `vendor/bearing-6707zz.step` | Bearing 6707ZZ (x1, joint 1) |
| bearing-6803zz | <img src="./doc/bearing-6803zz.svg" alt="bearing-6803zz" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 3 | chrome steel (AISI 52100) |  |  |  | amazon | B0D54JSWBZ | `vendor/bearing-6803zz.step` | Bearing 6803ZZ (x3) |
| bearing-axk5578 | <img src="./doc/bearing-axk5578.svg" alt="bearing-axk5578" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | chrome steel (AISI 52100) |  |  |  | amazon | B0B3M3RZGW | `vendor/bearing-axk5578.step` | Thrust bearing AXK5578 (x1, joint 1) |
| carriage-mgn9 | <img src="./doc/carriage-mgn9.svg" alt="carriage-mgn9" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | stainless steel |  |  |  | amazon | B0D9QBQDKB | `vendor/carriage-mgn9c.step` | Slider block MGN9 (x2, gripper) |
| finger | <img src="./doc/finger.svg" alt="finger" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Finger.step` | Gripper finger (x2); 0.4 mm nozzle, 0.2 mm layer height, 45% infill |
| flange | <img src="./doc/flange.svg" alt="flange" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 3 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_FLANGE.step` | Motor 2-4 rear flange (x3) |
| gear-connector | <img src="./doc/gear-connector.svg" alt="gear-connector" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Gear_Connector.step` | Gear connector (x1) |
| gear-m1-16t | <img src="./doc/gear-m1-16t.svg" alt="gear-m1-16t" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | steel |  |  |  | amazon | B0GDSR1LKM | `vendor/gear-m1-16t-b6.step` | Module 1, 16 tooth, 6 mm bore gear - what drives the two gripper racks (x1) |
| gripper-connector-a | <img src="./doc/gripper-connector-a.svg" alt="gripper-connector-a" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Gripper_Connector_A.step` | Gripper connector A (x1) |
| gripper-connector-b | <img src="./doc/gripper-connector-b.svg" alt="gripper-connector-b" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Gripper_Connector_B.step` | Gripper connector B (x1) |
| gripper-limit | <img src="./doc/gripper-limit.svg" alt="gripper-limit" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Lower_Arm_Limit.step` | Gripper horizontal limit (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| joint5-cable-restraint-a | <img src="./doc/joint5-cable-restraint-a.svg" alt="joint5-cable-restraint-a" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Joint5_Cable Restraint_A.step` | Motor 5 cable restraint (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| joint6-7-cable-restraint-a | <img src="./doc/joint6-7-cable-restraint-a.svg" alt="joint6-7-cable-restraint-a" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Joint6_7_Cable Restraint_A.step` | Motor 6 & 7 cable restraint A (x2); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| joint6-7-cable-restraint-b | <img src="./doc/joint6-7-cable-restraint-b.svg" alt="joint6-7-cable-restraint-b" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Joint6_7_Cable Restraint_B.step` | Motor 6 & 7 cable restraint B (x2); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| link1 | <img src="./doc/link1.svg" alt="link1" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/03_Link1.step` | Link 1 (x1) - CNC + sheet metal |
| link2 | <img src="./doc/link2.svg" alt="link2" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/03_Link2.step` | Link 2 (x2) - CNC + sheet metal |
| link3-l | <img src="./doc/link3-l.svg" alt="link3-l" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/03_Link3_L.step` | Link 3 left (x1) - CNC + sheet metal |
| link3-r | <img src="./doc/link3-r.svg" alt="link3-r" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/03_Link3_R.step` | Link 3 right (x1) - CNC + sheet metal |
| link5 | <img src="./doc/link5.svg" alt="link5" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/03_Link5.step` | Link 5 (x1) - CNC + sheet metal |
| lower-arm-cover | <img src="./doc/lower-arm-cover.svg" alt="lower-arm-cover" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Upper_Arm_Cover.step` | Lower arm cover (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| lower-arm-filler-l | <img src="./doc/lower-arm-filler-l.svg" alt="lower-arm-filler-l" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Lower_Arm_Filler_L.step` | Lower arm left filler (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| lower-arm-filler-m | <img src="./doc/lower-arm-filler-m.svg" alt="lower-arm-filler-m" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Lower_Arm_Filler_M.step` | Lower arm center filler (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| lower-arm-filler-r | <img src="./doc/lower-arm-filler-r.svg" alt="lower-arm-filler-r" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Lower_Arm_Filler_R.step` | Lower arm right filler (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| lower-upper-link-l | <img src="./doc/lower-upper-link-l.svg" alt="lower-upper-link-l" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Lower_Upper_Link_L.step` | Upper-lower arm link, left (x1) |
| lower-upper-link-r | <img src="./doc/lower-upper-link-r.svg" alt="lower-upper-link-r" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Lower_Upper_Link_R.step` | Upper-lower arm link, right (x1) |
| lower-wrist-link-l | <img src="./doc/lower-wrist-link-l.svg" alt="lower-wrist-link-l" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Lower_Wrist_Link_L.step` | Lower arm-wrist link, left (x1) |
| lower-wrist-link-r | <img src="./doc/lower-wrist-link-r.svg" alt="lower-wrist-link-r" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Lower_Wrist_Link_R.step` | Lower arm-wrist link, right (x1) |
| motor-back-spacer | <img src="./doc/motor-back-spacer.svg" alt="motor-back-spacer" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 3 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Motor_Back_Spacer.step` | Motor 2-4 rear spacer (x3) |
| motor-cover | <img src="./doc/motor-cover.svg" alt="motor-cover" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Motor_Cover.step` | Motor 5 protection cover (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| motor-front-spacer | <img src="./doc/motor-front-spacer.svg" alt="motor-front-spacer" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 4 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Motor_Front_Spacer.step` | Motor 2-5 front spacer (x4) - can be printed in ABS at 30% infill |
| pad-silicone | <img src="./doc/pad-silicone.svg" alt="pad-silicone" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | silicone |  |  |  | amazon | B0F9KVYXFZ | `vendor/pad-silicone-30x9x2.step` | Silicone pad 30x9x2mm (x1) |
| pin-d3x8 | <img src="./doc/pin-d3x8.svg" alt="pin-d3x8" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | stainless-steel |  |  |  |  |  | `vendor/pin-d3x8.step` | 3x8 mm dowel pin (x2) |
| pin-d4x10 | <img src="./doc/pin-d4x10.svg" alt="pin-d4x10" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 6 | stainless-steel |  |  |  | amazon | B0F6CWL4MP | `vendor/pin-d4x10.step` | 4x10 mm dowel pin (x6) |
| pin-d4x14 | <img src="./doc/pin-d4x14.svg" alt="pin-d4x14" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 3 | stainless-steel |  |  |  | amazon | B0F6CWL4MP | `vendor/pin-d4x14.step` | 4x14 mm dowel pin (x3) |
| pin-d4x7 | <img src="./doc/pin-d4x7.svg" alt="pin-d4x7" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 6 | stainless-steel |  |  |  | amazon | B0F6CWL4MP | `vendor/pin-d4x7.step` | 4x7 mm dowel pin (x6) |
| rack | <img src="./doc/rack.svg" alt="rack" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Rack.step` | Rack (x2) |
| rail-bracket | <img src="./doc/rail-bracket.svg" alt="rail-bracket" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Rail_Bracket.step` | Gripper slider support bracket (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| rail-mgn9-170 | <img src="./doc/rail-mgn9-170.svg" alt="rail-mgn9-170" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | stainless steel |  |  |  | amazon | B0D54L45WM | `vendor/rail-mgn9-170.step` | Linear rail MGN9-170mm (x1, gripper) |
| screw-hm3-12 | <img src="./doc/screw-hm3-12.svg" alt="screw-hm3-12" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 7 | stainless steel |  |  |  | amazon | B0DJQGMQZM (120 per pack) | `vendor/screw-hm3x12.step` | M3x12 hex socket head cap screw (x14+) |
| screw-hm3-25 | <img src="./doc/screw-hm3-25.svg" alt="screw-hm3-25" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 6 | stainless steel |  |  |  | amazon | B0DJQFGRPQ (120 per pack) | `vendor/screw-hm3x25.step` | M3x25 hex socket head cap screw (x14+) |
| screw-hm3-6 | <img src="./doc/screw-hm3-6.svg" alt="screw-hm3-6" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 8 | stainless steel |  |  |  | amazon | B0DJQG5YLF (120 per pack) | `vendor/screw-hm3x6.step` | M3x6 hex socket head cap screw (x16+) |
| screw-hm4-75 | <img src="./doc/screw-hm4-75.svg" alt="screw-hm4-75" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 4 | stainless steel |  |  |  | amazon | B0DR1NX178 | `vendor/screw-hm4x75.step` | M4x75 hex socket head screw (x4+) - README.md calls it a set screw |
| screw-ka3-12 | <img src="./doc/screw-ka3-12.svg" alt="screw-ka3-12" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 60 | steel |  |  |  | amazon | B01MXSS95N (100 per pack) | `vendor/screw-ka3x12.step` | KA3x12 self-tapping screw (x60; README.md says 72+) |
| screw-km3-12 | <img src="./doc/screw-km3-12.svg" alt="screw-km3-12" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 22 | stainless steel |  |  |  | amazon | B01E6EIC2S | `vendor/screw-km3x12.step` | M3x12 countersunk head screw (x30+) |
| screw-km3-16 | <img src="./doc/screw-km3-16.svg" alt="screw-km3-16" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 26 | stainless steel |  |  |  | amazon | B01E6EIC2S | `vendor/screw-km3x16.step` | M3x16 countersunk head screw (x34+) |
| screw-km3-7 | <img src="./doc/screw-km3-7.svg" alt="screw-km3-7" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 64 | stainless steel |  |  |  | amazon | B01E6EIC2S | `vendor/screw-km3x7.step` | M3x7 countersunk head screw (x76+) |
| screw-km3-8 | <img src="./doc/screw-km3-8.svg" alt="screw-km3-8" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 5 | stainless steel |  |  |  | amazon | B01MS60KSY | `vendor/screw-km3x8-micro.step` | M3x8 socket micro profile head screw (x31+) |
| screw-km3-9 | <img src="./doc/screw-km3-9.svg" alt="screw-km3-9" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 34 | stainless steel |  |  |  | amazon | B01E6EIC2S | `vendor/screw-km3x9.step` | M3x9 countersunk head screw (x31+) |
| screw-m4x5-set | <img src="./doc/screw-m4x5-set.svg" alt="screw-m4x5-set" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | steel |  |  |  |  |  | `vendor/screw-m4x5-set.step` | M4x5 set screw (x2); the released CAD calls it S-M4-5-JIMI and README.md does not list it |
| slider-bracket | <img src="./doc/slider-bracket.svg" alt="slider-bracket" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Slider_Bracket.step` | Gripper slider metal bracket (x1) - printable in ABS at high infill, not for long-term use |
| slider-extension | <img src="./doc/slider-extension.svg" alt="slider-extension" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 2 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Slider_Extension.step` | Slider to gripper extension (x2) |
| upper-arm-cover | <img src="./doc/upper-arm-cover.svg" alt="upper-arm-cover" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Lower_Arm_Cover.step` | Upper arm cover (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| upper-arm-filler-l | <img src="./doc/upper-arm-filler-l.svg" alt="upper-arm-filler-l" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Upper_Arm_Fuller_L.step` | Upper arm left filler (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| upper-arm-filler-m | <img src="./doc/upper-arm-filler-m.svg" alt="upper-arm-filler-m" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Upper_Arm_Fuller_M.step` | Upper arm center filler (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| upper-arm-filler-r | <img src="./doc/upper-arm-filler-r.svg" alt="upper-arm-filler-r" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | PLA | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Upper_Arm_Fuller_R.step` | Upper arm right filler (x1); 0.4 mm nozzle, 0.2 mm layer height, 15% infill |
| upper-arm-limit | <img src="./doc/upper-arm-limit.svg" alt="upper-arm-limit" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | ABS | additive |  | ±0.2 mm |  |  | `3D_Printed_Parts/01_Upper_Arm_Limit.step` | Upper arm horizontal limit block (x1); 0.4 mm nozzle, 0.2 mm layer height, 30% infill |
| wrist-bracket | <img src="./doc/wrist-bracket.svg" alt="wrist-bracket" style="width: auto; height: auto; max-width: 96px; max-height: 96px;"> | 1 | AL 5052 | subtractive | Anodized or sandblasted, H7 or interference fit on mating features | ±0.02 mm |  |  | `Metal_Parts/02_Wrist_Bracket.step` | Wrist motor 5 bracket (x1) |

## Stock

What the manufactured parts are made from: one piece for each part made from it.

### [//pub/robotics/rebot/devarm/b601-dm](README.md)

| Stock | Count | For | Description |
| --- | ---: | --- | --- |
| arm-yaw-limit-blank | 1 | arm-yaw-limit | The 5052 plate arm-yaw-limit is cut from |
| base-reinforcement-blank | 1 | base-reinforcement | The 5052 plate base-reinforcement is cut from |
| flange-blank | 3 | flange | The 5052 plate flange is cut from |
| gear-connector-blank | 1 | gear-connector | The 5052 plate gear-connector is cut from |
| gripper-connector-a-blank | 1 | gripper-connector-a | The 5052 plate gripper-connector-a is cut from |
| gripper-connector-b-blank | 1 | gripper-connector-b | The 5052 plate gripper-connector-b is cut from |
| link1-blank | 1 | link1 | The 5052 plate link1 is cut from |
| link2-blank | 2 | link2 | The 5052 plate link2 is cut from |
| link3-l-blank | 1 | link3-l | The 5052 plate link3-l is cut from |
| link3-r-blank | 1 | link3-r | The 5052 plate link3-r is cut from |
| link5-blank | 1 | link5 | The 5052 plate link5 is cut from |
| lower-upper-link-l-blank | 1 | lower-upper-link-l | The 5052 plate lower-upper-link-l is cut from |
| lower-upper-link-r-blank | 1 | lower-upper-link-r | The 5052 plate lower-upper-link-r is cut from |
| lower-wrist-link-l-blank | 1 | lower-wrist-link-l | The 5052 plate lower-wrist-link-l is cut from |
| lower-wrist-link-r-blank | 1 | lower-wrist-link-r | The 5052 plate lower-wrist-link-r is cut from |
| motor-back-spacer-blank | 3 | motor-back-spacer | The 5052 plate motor-back-spacer is cut from |
| motor-front-spacer-blank | 4 | motor-front-spacer | The 5052 plate motor-front-spacer is cut from |
| rack-blank | 2 | rack | The 5052 plate rack is cut from |
| slider-bracket-blank | 1 | slider-bracket | The 5052 plate slider-bracket is cut from |
| slider-extension-blank | 2 | slider-extension | The 5052 plate slider-extension is cut from |
| wrist-bracket-blank | 1 | wrist-bracket | The 5052 plate wrist-bracket is cut from |

<br/><br/>

*Generated by [PartCAD](https://partcad.org/)*
