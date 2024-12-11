from textx import metamodel_from_file
import tkinter as tk
from tkinter import scrolledtext


class StudentInterpreter:
    def __init__(self):
        self.classes = {}  # Stores class definitions
        self.instructions = []  # Stores instructions

    def interpret(self, model):
        # Process class definitions
        for class_def in model.classes:
            self.define_class(class_def)

        # Process instructions
        for instruction in model.instructions:
            self.process_instruction(instruction)

    def define_class(self, class_def):
        class_name = class_def.className
        if class_name in self.classes:
            print(f"Error: Class '{class_name}' is already defined.")
        else:
            self.classes[class_name] = {}

    def process_instruction(self, instruction):
        # Determine the type of instruction and handle accordingly
        instruction_type = instruction.__class__.__name__
        if instruction_type == "AssignmentType":
            self.handle_assignment_type(instruction)
        elif instruction_type == "Assignment":
            self.handle_assignment(instruction)
        elif instruction_type == "Calculate":
            self.handle_calculate(instruction)
        elif instruction_type == "Update":
            self.handle_update(instruction)
        elif instruction_type == "Delete":
            self.handle_delete(instruction)
        elif instruction_type == "Report":
            self.handle_report(instruction)

    def handle_assignment_type(self, assignment_type):
        class_name = assignment_type.className
        if class_name not in self.classes:
            print(f"Error: Class '{class_name}' is not defined.")
            return
        type_name = assignment_type.typeName
        weight = assignment_type.weight
        self.classes[class_name][type_name] = {"weight": weight, "assignments": []}

    def handle_assignment(self, assignment):
        class_name = assignment.className
        if class_name not in self.classes:
            print(f"Error: Class '{class_name}' is not defined.")
            return

        type_name = assignment.type
        if type_name not in self.classes[class_name]:
            print(f"Error: Type '{type_name}' is not defined for class '{class_name}'.")
            return

        name = assignment.name
        grade = assignment.grade
        self.classes[class_name][type_name]["assignments"].append({name: grade})

    def handle_calculate(self, calculate):
        # This function calculates grades. It can calculate:
        # -> A single assignment grade if assignmentName is provided
        # -> A type average and weighted grade if typeName is provided
        # -> The overall weighted grade of a class if only className is provided
        grade = 0

        if calculate.className:
            class_name = calculate.className
            if class_name not in self.classes:
                print(f"Error: Class '{class_name}' is not defined.")
                return

            if calculate.assignmentName:
                # Calculate a single assignment grade
                type_name = calculate.typeName
                assignment_name = calculate.assignmentName
                assignments = self.classes[class_name][type_name]["assignments"]
                if isinstance(assignments, list):
                    # Find the assignment by name in the list of dictionaries
                    for assignment in assignments:
                        if assignment_name in assignment:
                            print(f'{assignment[assignment_name]}')
                            break
                    else:
                        print(f"Error: No assignment named '{assignment_name}'.")
                else:
                    print(f"Error: No assignments for that '{type_name}'")
            elif calculate.typeName:
                # Calculate average and weighted grade for a specific type
                type_name = calculate.typeName
                if type_name not in self.classes[class_name]:
                    print(f"Error: Type '{type_name}' not defined in class '{class_name}'.")
                    return

                # Calculate average for this type
                data = self.classes[class_name][type_name]
                weight = data["weight"] * 0.01
                assignments = data["assignments"]
                sum_scores = 0
                count = 0
                for assignment in assignments:
                    for _, value in assignment.items():
                        sum_scores += value
                        count += 1
                average = sum_scores / count if count > 0 else 0
                totalWeighted = average * weight
                print(f"{type_name} Grade: {average} ---> Weighted Value: {totalWeighted}")
            else:
                # Calculate the overall weighted grade for the entire class
                for type_name, data in self.classes[class_name].items():
                    assignments = data.get('assignments', [])
                    sum_scores = 0
                    count = 0
                    for assignment in assignments:
                        for _, score in assignment.items():
                            sum_scores += score
                            count += 1
                    average = sum_scores / count if count > 0 else 0
                    totalWeighted = average * (data['weight'] * 0.01)
                    grade += totalWeighted
                print(f"{class_name} Weighted Grade: {grade}")

    def handle_update(self, update):
        # Update the grade of a specific assignment
        class_name = update.className
        if class_name not in self.classes:
            print(f"Error: Class '{class_name}' not found.")
            return

        type_name = update.type
        if type_name not in self.classes[class_name]:
            print(f"Error: Type '{type_name}' not found in class '{class_name}'.")
            return

        name = update.name
        new_grade = update.newGrade
        assignments = self.classes[class_name][type_name]["assignments"]
        updated = False
        for assignment in assignments:
            if name in assignment:
                assignment[name] = new_grade
                updated = True
                break

        if not updated:
            print(f"Error: Assignment '{name}' not found in type '{type_name}' for class '{class_name}'.")

    def handle_delete(self, delete):
        # Delete classes, types, or assignments based on the provided parameters
        class_name = delete.className
        if class_name not in self.classes:
            print(f"Error: Class '{class_name}' not found.")
            return

        # If typeName is specified, we check if we're deleting a type or an assignment
        if hasattr(delete, 'typeName') and delete.typeName:
            type_name = delete.typeName
            if type_name not in self.classes[class_name]:
                print(f"Error: Type '{type_name}' not found in class '{class_name}'.")
                return

            # If assignmentName is specified, delete a specific assignment
            if hasattr(delete, 'assignmentName') and delete.assignmentName:
                assignment_name = delete.assignmentName
                assignments = self.classes[class_name][type_name]["assignments"]
                found = False
                for i, assignment in enumerate(assignments):
                    if assignment_name in assignment:
                        assignments.pop(i)
                        found = True
                        break
                if not found:
                    print(f"Error: Assignment '{assignment_name}' not found in type '{type_name}' in class '{class_name}'.")
            else:
                # Delete the entire type
                del self.classes[class_name][type_name]
        else:
            # Delete the entire class
            del self.classes[class_name]

    def handle_report(self, report):
        # Display the report card in a popup window
        self.display_report_card_popup()

    def display_report_card_popup(self):
        # Create the popup window
        popup = tk.Tk()
        popup.title("Report Card")

        # Create a ScrolledText widget to display the report
        text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, width=80, height=30)
        text_area.pack(padx=10, pady=10)

        # Generate the report card content
        report_content = "=== Report Card ===\n"
        for class_name, types in self.classes.items():
            report_content += f"\nClass: {class_name}\n"
            report_content += "-" * (len(class_name) + 7) + "\n"
            class_total_weighted = 0
            for type_name, data in types.items():
                weight = data["weight"]
                assignments = data["assignments"]

                # Calculate type average
                sum_scores = 0
                num_assignments = 0
                for assignment in assignments:
                    for _, grade in assignment.items():
                        sum_scores += grade
                        num_assignments += 1
                average = sum_scores / num_assignments if num_assignments > 0 else 0
                weighted_average = average * (weight / 100)

                report_content += f"  Type: {type_name} (Weight: {weight}%)\n"
                report_content += f"    Average: {average:.2f}\n"
                report_content += f"    Weighted Average: {weighted_average:.2f}\n"

                # Print individual assignments
                for assignment in assignments:
                    for assignment_name, grade in assignment.items():
                        report_content += f"      - {assignment_name}: {grade}\n"

                class_total_weighted += weighted_average

            report_content += f"  Overall Weighted Grade: {class_total_weighted:.2f}\n"

        # Insert the content into the text widget
        text_area.insert(tk.END, report_content)
        text_area.config(state=tk.DISABLED)  # Make the text widget read-only

        # Start the Tkinter mainloop
        popup.mainloop()


if __name__ == "__main__":
    # Load the grammar
    student_mm = metamodel_from_file("student.tx")

    # Parse the input file
    model = student_mm.model_from_file("stephen.stud")

    # Create the interpreter
    interpreter = StudentInterpreter()

    # Interpret the model
    interpreter.interpret(model)
