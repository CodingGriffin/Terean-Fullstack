// export interface GeometryItem {
//     index: number,
//     x: number,
//     y: number,
//     z: number,
// }

// export interface GeometryArray {
//     units: string,
//     data: GeometryItem[]
// }

export interface Window {
    showSaveFilePicker(options?: {
        suggestedName?: string;
        types?: Array<{
            description: string;
            accept: Record<string, string[]>;
        }>;
    }): Promise<FileSystemFileHandle>;
}

export interface ContourData {
    type: string,
    rawInput: string,
    data: number | number[]
}

export interface CurrentUser {
    id: number,
    username: string,
    disabled: boolean,
    auth_level: number,
    email: string,
    full_name: string,
    expiration: DateTime | null,
}

export interface UserData {
    id: number,
    username: string,
    auth_level: number,
    email: string,
    full_name: string,
    expiration: DateTime | null,
}

export interface AdminUser extends UserData {
    id: number,
    disabled: boolean;
}
export interface State2dP {
    title: string,
    min_depth: string,
    max_depth: string,
    vel_min: string,
    vel_max: string,
    smoothing: string,
    x_min: string,
    x_max: string,
    y_label: string,
    x_label: string,
    cbar_label: string,
    label_pad_size: string,
    elevation_tick_increment: string,
    cbar_pad_size: string,
    contour_width: string,
    aboveground_color: string,
    aboveground_border_color: string,
    contour_color: string,
    contours: ContourData,
    invert_colorbar_axis: boolean,
    enable_colorbar: boolean,
    shift_elevation: boolean,
    display_as_depth: boolean,
    cbar_ticks: string[],
    reverse_elevation: boolean,
    reverse_data: boolean,
    unit_override: string,
    tick_right: boolean,
    tick_left: boolean,
    tick_top: boolean,
    tick_bottom: boolean,
    ticklabel_right: boolean,
    ticklabel_left: boolean,
    ticklabel_top: boolean,
    ticklabel_bottom: boolean,
    x_axis_label_pos: string,
    y_axis_label_pos: string,

}
