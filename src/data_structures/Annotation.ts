import { Point2D, Point3D } from "./Point";

export class Annotations {
    dst: string = null as unknown as string; // path to the video
    annotations: Array<FrameAnnotation> = null as unknown as Array<FrameAnnotation>;
    // placeholder_kpts: Array<Array<number>> = null as unknown as Array<Array<number>>; // placeholder keypoints

    constructor(dst: string, annotations: Array<FrameAnnotation>) {
        this.dst = dst;
        this.annotations = annotations;
    }

    static fromJSON(json: any): Annotations {
        let annotations = [];
        for (let i = 0; i < json.annotations.length; i++) {
            annotations.push(
                FrameAnnotation.fromJSON(json.annotations[i])
            );
        }
        return new Annotations(json.dst, annotations);
    }

    toJSON() {
        let annotations = [];
        for (let i = 0; i < this.annotations.length; i++) {
            annotations.push(
                this.annotations[i].toJSON()
            );
        }
        // console.log(annotations[0].visibles)
        return {
            dst: this.dst,
            annotations: annotations
        }
    }
}

export class FrameAnnotation {
    frame: number = null as unknown as number; // frame number

    // note: the following variable is only used for serialization; the actual visibility is stored in the joints_2d Point2D objects
    visibles: Array<boolean> = null as unknown as Array<boolean>; // whether the frame is visible or not (e.g. for occluded frames)

    names_2d: Array<string> = null as unknown as Array<string>;
    joints_2d: Array<Point2D> = null as unknown as Array<Point2D> // 2D coordinates of joints
    links_2d: Array<Array<number>> = null as unknown as Array<Array<number>>// links between joints
    confidences_2d: Array<number> = null as unknown as Array<number>// confidence for each joint
    format_2d: string = null as unknown as string;  // format of the annotation (e.g. coco, openpose, etc.)

    names_3d: Array<string> = null as unknown as Array<string>;
    joints_3d: Array<Point3D> = null as unknown as Array<Point3D>; // 3D coordinates of joints
    links_3d: Array<Array<number>> = null as unknown as Array<Array<number>>; // links between joints
    format_3d: string = null as unknown as string;  // format of the annotation (e.g. coco, openpose, etc.)

    selectedPoint: number = null as unknown as number; // index of the selected point

    constructor(
        frame: number,
        visibles: Array<boolean>,

        names_2d: Array<string>,
        joints_2d: Array<Point2D>,
        links_2d: Array<Array<number>>,
        confidences_2d: Array<number>,
        format_2d: string,
        names_3d: Array<string>,
        joints_3d: Array<Point3D>,
        links_3d: Array<Array<number>>,
        format_3d: string
    ) {
        this.frame = frame;
        this.visibles = visibles;

        this.names_2d = names_2d;
        this.joints_2d = joints_2d;
        this.links_2d = links_2d;
        this.confidences_2d = confidences_2d;
        this.format_2d = format_2d;

        this.names_3d = names_3d;
        this.joints_3d = joints_3d;
        this.links_3d = links_3d;
        this.format_3d = format_3d;

        this.selectedPoint = -1;
    }

    setSelected(selectedPoint: number) {
        this.selectedPoint = selectedPoint;
    }

    unsetSelected() {
        this.selectedPoint = -1;
    }

    resetVisibility() {
        this.joints_2d.forEach((joint) => {
            joint.visible = true;
        });
        for (let i = 0; i < this.visibles.length; i++) {
            this.visibles[i] = true;
        }
    }

    has3dData() {
        return this.joints_3d.length > 0;
    }

    toJSON() {
        let joints2d = [];
        for (let i = 0; i < this.joints_2d.length; i++) {
            // round to integers
            joints2d.push(
                [Math.round(this.joints_2d[i].x), Math.round(this.joints_2d[i].y)]
            );
        }
        let joints3d = [];
        for (let i = 0; i < this.joints_3d.length; i++) {
            joints3d.push(
                [this.joints_3d[i].x, this.joints_3d[i].y, this.joints_3d[i].z]
            );
        }
        let inferredVisibles = [];
        for (let i = 0; i < this.joints_2d.length; i++) {
            let isPointVis = this.joints_2d[i].visible;
            let sanityCheck = this.visibles[i];
            if (isPointVis != sanityCheck) {
                console.warn(
                    "Visibility of frame " + this.frame + " is inconsistent!",
                    "Joint " + i + " is " + isPointVis + " but frame is " + sanityCheck + "!"
                );
            }
            inferredVisibles.push(
                isPointVis
            );
        }

        return {
            frame: this.frame,
            visibles: inferredVisibles,
            names_2d: this.names_2d,
            joints_2d: joints2d,
            links_2d: this.links_2d,
            confidences_2d: this.confidences_2d,
            format_2d: this.format_2d,
            names_3d: this.names_3d,
            joints_3d: joints3d,
            links_3d: this.links_3d,
            format_3d: this.format_3d
        }
    }

    static fromJSON(json: any): FrameAnnotation {
        let joints2d = [];
        for (let i = 0; i < json.joints_2d.length; i++) {
            joints2d.push(
                new Point2D(
                    json.joints_2d[i][0],
                    json.joints_2d[i][1],
                    json.visibles[i]
                )
            );
        }
        let joints3d = [] as Array<Point3D>;
        for (let i = 0; i < json.joints_3d.length; i++) {
            joints3d.push(
                new Point3D(
                    json.joints_3d[i][0],
                    json.joints_3d[i][1],
                    json.joints_3d[i][2]
                )
            );
        }

        return new FrameAnnotation(
            json.frame,
            json.visibles,
            json.names_2d,
            joints2d,
            json.links_2d,
            json.confidences_2d,
            json.format_2d,
            json.names_3d,
            joints3d,
            json.links_3d,
            json.format_3d
        );
    }
}

