import { ShellFlyingLine } from "src/app/core/models/shell_flying_line.model";

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