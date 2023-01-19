export interface PersonView {
    id: number;
    name: string;
    assigned_org: string | null;
    quals: Map<string, string>;
}