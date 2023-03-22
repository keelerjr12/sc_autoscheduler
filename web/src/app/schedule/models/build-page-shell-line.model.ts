import { ShellFlyingLine, ShellDuty } from "src/app/core/models/shell_flying_line.model";

export class BuildPageShellLine {
    num: number;
    takeoff_time: string;
    assigned_org: string;

    constructor(shellLine : ShellFlyingLine) {
        this.num = shellLine.num;
        console.log(shellLine.start_date_time);
        this.takeoff_time = shellLine.start_date_time.split('T')[1];
        this.assigned_org = shellLine.org.name
    }
}

export class BuildPageShellDuty {
    id: number
    duty_id: number
    duty_type_id: number
    name: string
    start_date_time: string
    end_date_time: string

    constructor(shellDuty : ShellDuty) {
        this.id = shellDuty.id

        this.duty_id = shellDuty.duty.id
        this.duty_type_id = shellDuty.duty.duty_type_id
        this.name = shellDuty.duty.name

        this.start_date_time = shellDuty.start_date_time.split('T')[1];
        this.end_date_time = shellDuty.end_date_time.split('T')[1];
    }
}