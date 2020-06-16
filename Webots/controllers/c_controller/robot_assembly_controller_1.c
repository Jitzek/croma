/*
 * File:          robot_assembly_controller_1.c
 * Date:
 * Description:
 * Author:
 * Modifications:
 */

 //includes
#include <webots/robot.h>
#include <webots/touch_sensor.h>
#include <stdio.h>
#include <webots/keyboard.h>
#include <webots/motor.h>
#include <webots/camera.h>
#include <math.h>

//defines
#define wheelMotorSpeedStep 0.2
#define stabServoStep 0.2

#define stabalizeMeasurement 50
#define gravity 1.62
#define offsetMeasurement 1.077
#define plateWeight 0.0229
#define gearRatio (25/12)
#define smallgearSpeed 0.4166666666

//variables


double my_round(double x, unsigned int digits) {
	double fac = pow(10, digits);
	return round(x * fac) / fac;
}

int main(int argc, char** argv) {
	wb_robot_init();
	double time_step_World = wb_robot_get_basic_time_step();

	WbDeviceTag weight_sensor;
	weight_sensor = wb_robot_get_device("weight_measure");
	wb_touch_sensor_enable(weight_sensor, time_step_World);

	printf("Sensor type = %d\n", wb_touch_sensor_get_type(weight_sensor));

	WbDeviceTag camera;
	camera = wb_robot_get_device("camera");

	char arm_servos[6][12] = { "arm_servo_1","arm_servo_2", "arm_servo_3", "arm_servo_4", "arm_servo_5" , "arm_servo_6" };
	WbDeviceTag armServo_tag[8];
	for (int i = 0; i < 6; i++) {
		armServo_tag[i] = wb_robot_get_device(arm_servos[i]);
		printf("%s has got tag %i\n", arm_servos[i], armServo_tag[i]);
	}

	char wheel_motors[6][8] = { "wheel_1","wheel_2", "wheel_3", "wheel_4", "wheel_5", "wheel_6" };
	WbDeviceTag wheel_motor_tag[6];
	for (int i = 0; i < 6; i++) {
		wheel_motor_tag[i] = wb_robot_get_device(wheel_motors[i]);
		wb_motor_set_position(wheel_motor_tag[i], INFINITY);
		//wb_motor_set_torque(wheel_motor_tag, 0.01);
		printf("%s has got tag %i\n", wheel_motors[i], wheel_motor_tag[i]);
	}
	//wb_motor_set_position(wheel_motor_tag[0], INFINITY);
	//wb_motor_set_torque(wheel_motor_tag[0], 1);
	//wb_motor_set_position(wheel_motor_tag[1], INFINITY);
	//wb_motor_set_position(wheel_motor_tag[2], INFINITY);
	//wb_motor_set_position(wheel_motor_tag[3], INFINITY);
	//wb_motor_set_torque(wheel_motor_tag[3], 1);
	//wb_motor_set_position(wheel_motor_tag[4], INFINITY);
	//wb_motor_set_position(wheel_motor_tag[5], INFINITY);



	wb_keyboard_enable(time_step_World);
	unsigned int pressed_Key = 0;
	unsigned int temp1 = 0;
	bool sendOnce = true, keyReleased = true;

	double measured = 0, weightOffset = 0;

	double wheel_motor_speed[6] = { 0,0,0,0,0,0 };//{ wheelMotorSpeedStep,wheelMotorSpeedStep,wheelMotorSpeedStep,-wheelMotorSpeedStep,-wheelMotorSpeedStep,-wheelMotorSpeedStep };
	double arm_servo_Position[6] = { 0,0,0,0,0 };

	wb_camera_enable(camera, time_step_World);

	printf("controller has started\n");
	while (wb_robot_step(time_step_World) != -1) {

		pressed_Key = wb_keyboard_get_key();

		if (keyReleased) {
			double totalMeasurement = 0;
			switch (pressed_Key) {
			case 'Q':
				if (wheel_motor_speed[0] < 2) {
					for (int i = 0; i < 3; i++) {
						wheel_motor_speed[i] += wheelMotorSpeedStep;
					}
					sendOnce = true;
				}

				break;
			case 'A':
				if (wheel_motor_speed[0] > -2) {
					for (int i = 0; i < 3; i++) {
						wheel_motor_speed[i] -= wheelMotorSpeedStep;
					}
					sendOnce = true;
				}
				break;
			case 'S':
				if (wheel_motor_speed[3] < 2) {
					for (int i = 3; i < 6; i++) {
						wheel_motor_speed[i] += wheelMotorSpeedStep;
					}
					sendOnce = true;
				}
				break;
			case 'W':
				if (wheel_motor_speed[3] > -2) {
					for (int i = 3; i < 6; i++) {
						wheel_motor_speed[i] -= wheelMotorSpeedStep;
					}
					sendOnce = true;
				}
				break;
			case 'E':
				if (arm_servo_Position[0] < 1.5) {
					arm_servo_Position[0] += stabServoStep;
					sendOnce = true;
				}
				break;
			case 'D':
				if (arm_servo_Position[0] > -1.5) {
					arm_servo_Position[0] -= stabServoStep;
					sendOnce = true;
				}
				break;

			case 'R':
				if (arm_servo_Position[1] < 2.4) {
					arm_servo_Position[1] += stabServoStep;
					sendOnce = true;
				}
				break;
			case 'F':
				if (arm_servo_Position[1] > -2.4) {
					arm_servo_Position[1] -= stabServoStep;
					sendOnce = true;
				}
				break;
			case 'T':
				if (arm_servo_Position[2] < 2.4) {
					arm_servo_Position[2] += stabServoStep;
					sendOnce = true;
				}
				break;
			case 'G':
				if (arm_servo_Position[2] > -2.4) {
					arm_servo_Position[2] -= stabServoStep;
					sendOnce = true;
				}
				break;
			case 'Y':
				if (arm_servo_Position[3] < 2.4) {
					arm_servo_Position[3] += stabServoStep;
					arm_servo_Position[4] -= stabServoStep;
					sendOnce = true;
				}
				break;
			case 'H':
				if (arm_servo_Position[3] > -2.4) {
					arm_servo_Position[3] -= stabServoStep;
					arm_servo_Position[4] += stabServoStep;
					sendOnce = true;
				}
				break;
			case 'U':
				if (arm_servo_Position[4] < 2.4) {
					arm_servo_Position[4] += stabServoStep;
					printf("gear step = %f\n", (stabServoStep * gearRatio));
					arm_servo_Position[5] += smallgearSpeed;
					sendOnce = true;
				}
				break;
			case 'J':
				if (arm_servo_Position[4] > -2.4) {
					arm_servo_Position[4] -= stabServoStep;
					arm_servo_Position[5] -= smallgearSpeed;
					sendOnce = true;
				}
				break;
			case 'I':
				if (arm_servo_Position[5] < 2.4) {
					arm_servo_Position[5] += stabServoStep;
					sendOnce = true;
				}
				break;
			case 'K':
				if (arm_servo_Position[5] > -2.4) {
					arm_servo_Position[5] -= stabServoStep;
					sendOnce = true;

				}
				break;
			case 'O':
				measured = (wb_touch_sensor_get_value(weight_sensor));
				printf("Measured = %f N\n", measured);
				weightOffset = measured;
				printf("Set weightOffset = %f\n", weightOffset);
				break;
			case 'L':
				measured = (wb_touch_sensor_get_value(weight_sensor));
				printf("Measured = %f N\n", measured);
				printf("Set weightOffset = %f\n", weightOffset);
				measured -= weightOffset;
				printf("Measured-offset = %f N\n", measured);
				printf("Measured calibrated = %f kg\n", measured / 63.7);
				break;
			case 'P':
				for (int p = 0; p < stabalizeMeasurement; p++) {					//measure weight stabalizeMeasurement times
					measured = (wb_touch_sensor_get_value(weight_sensor));
					totalMeasurement += measured;									//save in totalMeasurement
				}
				measured = totalMeasurement / stabalizeMeasurement;					//divide total by stabalizeMeasurement
				measured = measured - plateWeight;									//minus the weight of the scale itself
				measured *= gravity;												//translate force to weight by multipy with gravity
				measured *= offsetMeasurement;										//multiply with the calculated offset
				measured = my_round(measured, 3);									//round variabel to grams
				printf("Measured(with offset and rounded) = %2.3f kg\n", measured);	//put it to the console
				break;
			case 'Z':
				printf("Arm to drive position\n");
				arm_servo_Position[0] = 1.6;
				arm_servo_Position[1] = 0;
				arm_servo_Position[2] = -.7;
				arm_servo_Position[3] = 1.4;
				arm_servo_Position[4] = -1.4;
				arm_servo_Position[5] = 0;
				sendOnce = true;
				break;
			case 'X':
				printf("Arm to drive position\n");
				arm_servo_Position[0] = 0;
				arm_servo_Position[1] = 0;
				arm_servo_Position[2] = 0;
				arm_servo_Position[3] = 0;
				arm_servo_Position[4] = 0;
				arm_servo_Position[5] = 0;
				sendOnce = true;
				break;
			case 'C':
				printf("Arm to get position\n");
				arm_servo_Position[0] = -1;
				arm_servo_Position[1] = 0.8;
				arm_servo_Position[2] = 1.2;
				arm_servo_Position[3] = 0;
				arm_servo_Position[4] = 0;
				arm_servo_Position[5] = 0;
				sendOnce = true;
				break;
			case 'V':
				printf("Arm to drop weight measure position\n");
				arm_servo_Position[0] = 0;
				arm_servo_Position[1] = -1.2;
				arm_servo_Position[2] = -1.3;
				arm_servo_Position[3] = 1.2;
				sendOnce = true;
				break;
			case 'M':
				printf("Disable wheel motors\n");
				for (int i = 0; i < 6; i++) {
					wheel_motor_speed[i] = 0;
				}
				sendOnce = true;
				break;

			}
		}
		//printf("pressed_Key = %i\n", pressed_Key);

		if ((!keyReleased) & (pressed_Key == -1)) {
			keyReleased = true;
			//printf("key released = true\n");
		}
		else if (pressed_Key != -1) {
			keyReleased = false;
		}

		if (sendOnce) {
			sendOnce = false;
			for (int j = 0; j < 6; j++)
			{
				wb_motor_set_velocity(wheel_motor_tag[j], wheel_motor_speed[j]);
				printf("Speed %i = %f\n", j, wheel_motor_speed[j]);
			}
			for (int p = 0; p < 6; p++)
			{
				wb_motor_set_position(armServo_tag[p], arm_servo_Position[p]);
				wb_motor_set_velocity(armServo_tag[p], 0.5);
				printf("Position %i = %f\n", p, arm_servo_Position[p]);
			}
			wb_motor_set_velocity(armServo_tag[5], (0.5 * (25 / 12)));//(0.5*(25/12))
		}

	};

	wb_robot_cleanup();

	return 0;
}
