/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/*
 * JFrameRotSpectra.java
 *
 * Created on 22-abr-2010, 12:35:07
 */
package xmipp.viewer.gallery;

import xmipp.viewer.gallery.models.GalleryRowHeaderModel;
import xmipp.viewer.gallery.models.MDTableModel;
import xmipp.viewer.gallery.models.GalleryTableColumnModel;
import xmipp.viewer.imageitems.tableitems.AbstractGalleryImageItem;
import xmipp.viewer.gallery.renderers.ImageRenderer;
import xmipp.viewer.gallery.renderers.RowHeaderRenderer;
import xmipp.viewer.windows.ImagesWindowFactory;
import xmipp.utils.DEBUG;
import xmipp.utils.Labels;
import xmipp.viewer.gallery.models.AbstractXmippTableModel;
import xmipp.viewer.gallery.models.VolumeTableModel;
import ij.IJ;
import ij.ImagePlus;
import ij.WindowManager;

import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.InputEvent;
import java.awt.event.ItemEvent;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.File;
import java.util.Timer;
import java.util.TimerTask;

import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPopupMenu;
import javax.swing.JSpinner;
import javax.swing.JToggleButton;
import javax.swing.KeyStroke;
import javax.swing.LookAndFeel;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingUtilities;
import javax.swing.border.Border;
import xmipp.jni.Filename;
import xmipp.jni.ImageGeneric;
import xmipp.jni.MetaData;
import xmipp.ij.XmippImageConverter;
import xmipp.utils.Resources;

/**
 *
 * @author Juanjo Vega
 */
public class JFrameGallery extends JFrame 
	implements MouseListener {

    private final static int DELAY_TO_UPDATE = 500;
    private static int update_counter = 0;
    private AbstractXmippTableModel tableModel;
    private GalleryTableColumnModel columnModel;
    private GalleryRowHeaderModel rowHeaderModel;
    private int previousSelectedRow, previousSelectedCol;
    private JList rowHeader;
    private ImageRenderer renderer = new ImageRenderer();
    private Timer updateTimer = new Timer(true);    // Timer for zoom.
    private TableUpdater tableUpdaterTask;    // Associated task for zoom timer.
    private boolean isUpdating;
    //this flag will be used to avoid firing properties change events
    //when the change is from our code and not external user interaction
    private boolean internalChange = false; 
    private boolean autoAdjustColumns = false;
    private JPopUpMenuGallery jpopUpMenuTable;
    private JMenuBarTable jMenuBarTable;
    JFileChooser fc = new JFileChooser();

    public enum RESLICE_MODE {

        TOP_Y, RIGHT_X
    }

    public JFrameGallery(String filename) {
        super();

        try {
            boolean volume = Filename.isVolume(filename);
            createGUI(volume ? new VolumeTableModel(filename) : new MDTableModel(filename));
        } catch (Exception e) {
            DEBUG.printException(e);
            IJ.error(e.getMessage());
        }
    }

    public JFrameGallery(String filenames[]) {
        this(filenames, null);
    }

    public JFrameGallery(String filenames[], boolean enabled[]) {
        super();
        createGUI(new MDTableModel(filenames, enabled));
    }

    
    /**
     * Function to create general GUI base on a TableModel.
     * It will use helper functions to create different 
     * components of the GUI
     */
    private void createGUI(AbstractXmippTableModel tm) {
    	isUpdating = true; //avoid handling some changes events
    	tableModel = tm;
    	
    	setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    	
    	//Register some listeners
        addWindowListener(new java.awt.event.WindowAdapter() {
            public void windowOpened(java.awt.event.WindowEvent evt) {
                formWindowOpened(evt);
            }
        });
        
        addComponentListener(new java.awt.event.ComponentAdapter() {
            public void componentResized(java.awt.event.ComponentEvent evt) {
                formComponentResized(evt);
            }
        });
    	
       // addMouseListener(l)
        
        jMenuBarTable = new JMenuBarTable();
        setJMenuBar(jMenuBarTable);

        columnModel = new GalleryTableColumnModel();

        initComponents();

        table.setColumnModel(columnModel);
        table.setDefaultRenderer(AbstractGalleryImageItem.class, renderer);

        setTitle(tableModel.getTitle());

        jpopUpMenuTable = new JPopUpMenuGallery();

        // Sets limits for spinners.
        jsRows.setModel(new SpinnerNumberModel(1, 1, tableModel.getSize(), 1));
        jsColumns.setModel(new SpinnerNumberModel(1, 1, tableModel.getSize(), 1));
        jsGoToImage.setModel(new SpinnerNumberModel(1, 1, tableModel.getSize(), 1));

        setRowHeader();

        int TEXTWIDTH = 4;
        ((JSpinner.NumberEditor) jsZoom.getEditor()).getTextField().setColumns(TEXTWIDTH);
        ((JSpinner.NumberEditor) jsGoToImage.getEditor()).getTextField().setColumns(TEXTWIDTH);
        ((JSpinner.NumberEditor) jsRows.getEditor()).getTextField().setColumns(TEXTWIDTH);
        ((JSpinner.NumberEditor) jsColumns.getEditor()).getTextField().setColumns(TEXTWIDTH);

//        jpDisplay.setLayout(new SpringLayout());
//        SpringUtilities.makeCompactGrid(jpDisplay, 1, 7, 0, 0, 3, 3);
//        jpBottom.setLayout(new SpringLayout());
//        SpringUtilities.makeCompactGrid(jpBottom, 1, 5, 0, 0, 3, 3);

        // Stacks will be "auto-normalized".
        setNormalized(tableModel.isVolume());

        // Geometry info is used if present, otherwise button is disabled.
        boolean containsGeometry = tableModel.containsGeometryInfo();
        //tableModel.setUseGeometry(jtbUseGeometry.isSelected());
        jtbUseGeometry.setSelected(containsGeometry);
        jtbUseGeometry.setEnabled(containsGeometry);
        
        // Set comboBox items.
        String labels[] = tableModel.getLabels();
        for (int i = 0; i < labels.length; i++) {
            jcbMDLabels.addItem(labels[i]);
        }
        
        isUpdating = false; 
        //startUpdater();
        pack();
        ImagesWindowFactory.setConvenientSize(this);
    }

    private void createMenu(){
    	
    }
    
    private void setRowHeader() {
        rowHeaderModel = new GalleryRowHeaderModel(table, 1);

        rowHeader = new JList();
        rowHeader.setModel(rowHeaderModel);

        LookAndFeel.installColorsAndFont(rowHeader, "TableHeader.background",
                "TableHeader.foreground", "TableHeader.font");

        rowHeader.setCellRenderer(new RowHeaderRenderer());

        jspContent.setRowHeaderView(rowHeader);
        rowHeader.repaint();
    }

    private void updateTable() {
//        if (table.isShowing()) {
    	boolean updatingState = isUpdating;
        isUpdating = true;
        update_counter++;
        DEBUG.printMessage(" *** Updating table: " + update_counter);//System.currentTimeMillis() );
        DEBUG.printStackTrace();

        tableModel.updateSort();

        if (tableModel.getSize() > 0) {
        	DEBUG.printMessage("TABLEMODEL SIZE > 0");
            Dimension dimension = getCellSize();
            renderer.setPreferredSize(dimension);

            // Adjusts rows size.
            table.setRowHeight(dimension.height > 0 ? dimension.height : 1);
            rowHeader.setFixedCellHeight(table.getRowHeight());
//            rowHeader.setFixedCellWidth(rowHeader.getModel().getSize() * 2);
            columnModel.setWidth(dimension.width > 0 ? dimension.width : 1);

            // If auto adjust columns is enabled, refresh!
            if (autoAdjustColumns) {
                autoAdjustColumns();
            }

            rowHeader.repaint();
            table.revalidate();
        }

        isUpdating = updatingState;
//        }
    }

    private Dimension getCellSize() {
        int font_height = 0;
        if (tableModel.isShowingLabels()) {
            font_height = renderer.getFontMetrics(renderer.getFont()).getHeight();
            font_height += renderer.getIconTextGap();  // Adds the extra gap.
            font_height -= table.getIntercellSpacing().height;   // Removes spacing.
        }

        int borderHeight = 0, borderWidth = 0;
        Border border = renderer.getBorder();

        if (border != null) {
            Insets insets = renderer.getBorder().getBorderInsets(renderer);
            borderWidth = insets.left + insets.right;
            borderHeight = insets.bottom + insets.top;
        }

        return new Dimension(
                tableModel.getCellWidth() + 2 * borderWidth,
                tableModel.getCellHeight() + font_height + 2 * borderHeight);
    }

    private void startUpdater() {
    	
        if (tableUpdaterTask == null) {
        	tableUpdaterTask = new TableUpdater();
        	updateTimer.schedule(tableUpdaterTask, DELAY_TO_UPDATE);
        }

    }
//
//    private void setShowLabels(boolean show) {
//        tableModel.setShowLabels(show);
//
////        startUpdater();
//        updateTable();
//    }
//
//    private void updateLabelToShow(int index) {
//        tableModel.setSelectedLabel(index);
//
//        updateTable();
//    }

    private void autoAdjustColumns() {
        tableModel.autoAdjustColumns(
                //jsPanel.getVisibleRect().width - rowHeader.getWidth(),
                //jsPanel.getViewportBorderBounds().width - rowHeader.getWidth(),
                jspContent.getViewport().getWidth() - rowHeader.getWidth(),
                table.getIntercellSpacing().width);

        jsRows.setValue(tableModel.getRowCount());
        jsColumns.setValue(tableModel.getColumnCount());
    }

    private void setInitialValues() {
        if (tableModel.getSize() > 0) {
            double scale = tableModel.getInitialZoomScale(
                    jspContent.getVisibleRect().width,
                    table.getIntercellSpacing().width);
            setZoom((int) (scale * 100));
        } else {
            jsZoom.setEnabled(false);
            jcbAutoAdjustColumns.setEnabled(false);
            jcbShowLabels.setEnabled(false);
            jsRows.setEnabled(false);
            jsColumns.setEnabled(false);
            jsGoToImage.setEnabled(false);
        }
    }

    private void setZoom(int zoom) {
        tableModel.setZoomScale(zoom / 100.0);
        jsZoom.setValue(zoom);
    }

    public void setDimensions(int rows, int columns) {
        setAutoAdjustColumns(false);
        setRowsValue(rows);
        setColumnsValue(columns);
    }

    void setRowsValue(int rows) {
        if (rows > 0) {
            tableModel.setRows(rows);
            jsColumns.setValue(tableModel.getColumnCount());
        }
    }

    void setColumnsValue(int columns) {
        if (columns > 0) {
            tableModel.setColumns(columns);
            jsRows.setValue(tableModel.getRowCount());
        }
    }

    public void enableAutoadjustColumns(boolean enable) {
        jcbAutoAdjustColumns.setSelected(enable);
    }

    public void setAutoAdjustColumns(boolean autoAdjustColumns) {
        this.autoAdjustColumns = autoAdjustColumns;
        jcbAutoAdjustColumns.setSelected(autoAdjustColumns);
        jsColumns.setEnabled(!autoAdjustColumns);
        jsRows.setEnabled(!autoAdjustColumns);
    }

    private void goToImage(int index) {
        tableModel.setSelected(index);

        int coords[] = tableModel.getRowColForIndex(index);

        // Gets current selected cell bounds.
        Rectangle rect = table.getCellRect(coords[0], coords[1], true);

        // Ensures item is visible.
        Point pos = jspContent.getViewport().getViewPosition();
        rect.translate(-pos.x, -pos.y);
        jspContent.getViewport().scrollRectToVisible(rect);

        repaint();
    }

    private void avgImage() {
        ImagesWindowFactory.captureFrame(ImageOperations.mean(tableModel.getAllItems()));
    }

    private void stdDevImage() {
        ImagesWindowFactory.captureFrame(ImageOperations.std_deviation(tableModel.getAllItems()));
    }

    private void setNormalized(boolean normalize) {
        jtbNormalize.setSelected(normalize);
        tableModel.setNormalized(normalize);
    }

    private void openAsStack() {
        ImagesWindowFactory.openGalleryAsImagePlus(tableModel);
    }

    private void openAs3D() {
        ImagesWindowFactory.openGalleryAs3D(tableModel);
    }

    private void saveAsMetadata(boolean all) {
        // Sets path and filename automatically.
        String filename = tableModel.getFilename() != null ? tableModel.getFilename() : "";
        fc.setSelectedFile(new File(forceExtension(filename, ".xmd")));

        if (fc.showSaveDialog(this) != JFileChooser.CANCEL_OPTION) {
            boolean response = true;
            if (fc.getSelectedFile().exists()) {
                response = JOptionPane.showConfirmDialog(null,
                        Labels.MESSAGE_OVERWRITE_FILE,
                        Labels.MESSAGE_OVERWRITE_FILE_TITLE,
                        JOptionPane.OK_CANCEL_OPTION,
                        JOptionPane.QUESTION_MESSAGE) == JOptionPane.OK_OPTION;
            }

            if (response) {
                String path = fc.getSelectedFile().getAbsolutePath();
                if (tableModel.saveAsMetadata(path, all)) {
                    JOptionPane.showMessageDialog(this, Labels.MESSAGE_FILE_SAVED + path,
                            Labels.MESSAGE_FILE_SAVED_TITLE, JOptionPane.INFORMATION_MESSAGE);
                }
            }
        }
    }

    private void saveAsStack(boolean all) {
        // Sets path and filename automatically.
        String filename = tableModel.getFilename() != null ? tableModel.getFilename() : "";
        fc.setSelectedFile(new File(forceExtension(filename, ".stk")));

        if (fc.showSaveDialog(this) != JFileChooser.CANCEL_OPTION) {
            boolean response = true;
            if (fc.getSelectedFile().exists()) {
                response = JOptionPane.showConfirmDialog(null,
                        Labels.MESSAGE_OVERWRITE_FILE,
                        Labels.MESSAGE_OVERWRITE_FILE_TITLE,
                        JOptionPane.OK_CANCEL_OPTION,
                        JOptionPane.QUESTION_MESSAGE) == JOptionPane.OK_OPTION;
            }

            if (response) {
                String path = fc.getSelectedFile().getAbsolutePath();
                if (tableModel.saveAsStack(path, all)) {
                    JOptionPane.showMessageDialog(this, Labels.MESSAGE_FILE_SAVED + path,
                            Labels.MESSAGE_FILE_SAVED_TITLE, JOptionPane.INFORMATION_MESSAGE);
                }
            }
        }
    }

    static String forceExtension(String filename, String ext) {
        int dot = filename.lastIndexOf(".");
        return filename.substring(0, dot) + ext;
    }

    public void pca() {
        String filename = tableModel.getFilename();

        try {
            MetaData md = new MetaData(filename);
            ImageGeneric image = new ImageGeneric();

            md.getPCAbasis(image);

            ImagePlus imp = XmippImageConverter.convertToImageJ(image);
            imp.setTitle("PCA: " + filename);
            ImagesWindowFactory.captureFrame(imp);
        } catch (Exception ex) {
            DEBUG.printException(ex);
        }
    }

    public void fsc() {
        String filename = tableModel.getFilename();

        try {
            MetaData md = new MetaData(filename);

            ImagesWindowFactory.openFSCWindow(filename);
        } catch (Exception ex) {
            DEBUG.printException(ex);
        }
    }

    private void reslice(RESLICE_MODE mode) throws Exception {
        String command = null;

        switch (mode) {
            case TOP_Y:
                command = "Top";
                break;
            case RIGHT_X:
                command = "Right";
                break;
        }

        // Get volume ImagePlus.
        String filename = tableModel.getFilename();
        ImagePlus volume = XmippImageConverter.loadImage(filename);

        // Reslice.
        IJ.run(volume, "Reslice [/]...", "slice=1.000 start=" + command);
        volume = WindowManager.getCurrentImage();
        volume.getWindow().setVisible(false);

        // Save temp file.
        int index = filename.lastIndexOf(".");
        String name = filename.substring(filename.lastIndexOf(File.separator) + 1, index);
        String ext = filename.substring(index);
        File f = File.createTempFile(name + "_" + command, ext);
        f.deleteOnExit();

        XmippImageConverter.saveImage(volume, f.getAbsolutePath());
        volume.close();

        // Open as gallery.
        ImagesWindowFactory.openFileAsGallery(f.getCanonicalPath());
    }

    /***
     * Helper function to create toolbar toggle buttons
     */
    protected JToggleButton createToggleButton(String icon, String text, ActionListener listener){
        //Add toggle button to set/unset global normalization
        JToggleButton toggleBtn = new javax.swing.JToggleButton();
        toggleBtn.setFocusable(false);
        toggleBtn.setIcon(Resources.getIcon(icon));
        toggleBtn.setToolTipText(text);
        toggleBtn.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        toggleBtn.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        toggleBtn.addActionListener(listener);        
        return toggleBtn;
    }
    
    /***
     * Function to create the main toolbar
     */
    protected void createToolbar(){
        //Create Main TOOLBAR
        toolBar = new javax.swing.JToolBar();
        toolBar.setRollover(true);
        toolBar.setLayout(new FlowLayout(FlowLayout.LEFT));
        //toolBar.setLayout(new BoxLayout(toolBar, BoxLayout.X_AXIS));
        
        //Add toggle button to set/unset global normalization
        jtbNormalize = createToggleButton(Resources.NORMALIZE, Labels.MSG_NORMALIZE, 
        		new java.awt.event.ActionListener() {
            	public void actionPerformed(java.awt.event.ActionEvent evt) {
            		jtbNormalizeActionPerformed(evt);
            	}} );
        toolBar.add(jtbNormalize);
        //Add toggle button to set/unset apply geometry when read from metadata
        jtbUseGeometry = createToggleButton(Resources.APPLY_GEO, Labels.MSG_APPLY_GEO, 
        		new java.awt.event.ActionListener() {
            	public void actionPerformed(java.awt.event.ActionEvent evt) {
            		jtbUseGeometryActionPerformed(evt);
            	}} );        
        toolBar.add(jtbUseGeometry);
        
        toolBar.addSeparator();
        //jLabel1.setText(LABELS.LABEL_ZOOM);
        jlZoom.setIcon(Resources.getIcon("zoom.png"));
        toolBar.add(jlZoom);
        
        jsZoom.setModel(new javax.swing.SpinnerNumberModel(Integer.valueOf(1), Integer.valueOf(1), null, Integer.valueOf(1)));
        jsZoom.addChangeListener(new javax.swing.event.ChangeListener() {
        	public void stateChanged(javax.swing.event.ChangeEvent evt) {
        		jsZoomStateChanged(evt);
        	}
        });
        toolBar.add(jsZoom);   
        
        toolBar.addSeparator();
        
        //TODO: MOVE THIS TO MENU OPTION
//        jcbShowLabels.setText(Labels.LABEL_SHOW_LABELS);
//        jcbShowLabels.addActionListener(new java.awt.event.ActionListener() {
//            public void actionPerformed(java.awt.event.ActionEvent evt) {
//                jcbShowLabelsActionPerformed(evt);
//            }
//        });
//        toolBar.add(jcbShowLabels);
//
//        jcbMDLabels.addItemListener(new java.awt.event.ItemListener() {
//            public void itemStateChanged(java.awt.event.ItemEvent evt) {
//                jcbMDLabelsItemStateChanged(evt);
//            }
//        });
//        toolBar.add(jcbMDLabels);
//
//        jcbSortByLabel.setText(Labels.LABEL_SORT_BY_LABEL);
//        jcbSortByLabel.addActionListener(new java.awt.event.ActionListener() {
//            public void actionPerformed(java.awt.event.ActionEvent evt) {
//                jcbSortByLabelActionPerformed(evt);
//            }
//        });
//        toolBar.add(jcbSortByLabel);

        jlGoto.setIcon(Resources.getIcon("goto.gif"));
        jlGoto.setToolTipText(Labels.LABEL_GOTO_ITEM);
        toolBar.add(jlGoto);

        jsGoToImage.setValue(1);
        jsGoToImage.addChangeListener(new javax.swing.event.ChangeListener() {
            public void stateChanged(javax.swing.event.ChangeEvent evt) {
                jsGoToImageStateChanged(evt);
            }
        });
        toolBar.add(jsGoToImage);
        
        toolBar.addSeparator();
        
        
        jcbAutoAdjustColumns = createToggleButton(Resources.ADJUST_COLS, Labels.MSG_ADJUST_COLS, 
        		new java.awt.event.ActionListener() {
        		public void actionPerformed(java.awt.event.ActionEvent evt) {
        			jcbAutoAdjustColumnsStateChanged(evt);
        	}} );  
        jlRows = new javax.swing.JLabel();
        jsRows = new javax.swing.JSpinner();
        jlColumns = new javax.swing.JLabel();
        jsColumns = new javax.swing.JSpinner();
        toolBar.add(jcbAutoAdjustColumns);

        jlColumns.setText(Labels.LABEL_COLUMNS);
        toolBar.add(jlColumns);
        
        jsColumns.addChangeListener(new javax.swing.event.ChangeListener() {
        	public void stateChanged(javax.swing.event.ChangeEvent evt) {
        		jsColumnsStateChanged(evt);
        	}
        });
        toolBar.add(jsColumns);
        
        jlRows.setText(Labels.LABEL_ROWS);
        toolBar.add(jlRows);

        jsRows.addChangeListener(new javax.swing.event.ChangeListener() {
            public void stateChanged(javax.swing.event.ChangeEvent evt) {
                jsRowsStateChanged(evt);
            }
        });
        toolBar.add(jsRows);
        
        // Some settings of the spinners
        jsRows.setModel(new SpinnerNumberModel(1, 1, tableModel.getSize(), 1));
        jsColumns.setModel(new SpinnerNumberModel(1, 1, tableModel.getSize(), 1));
        jsGoToImage.setModel(new SpinnerNumberModel(1, 1, tableModel.getSize(), 1));

        int TEXTWIDTH = 4;
        ((JSpinner.NumberEditor) jsZoom.getEditor()).getTextField().setColumns(TEXTWIDTH);
        ((JSpinner.NumberEditor) jsGoToImage.getEditor()).getTextField().setColumns(TEXTWIDTH);
        ((JSpinner.NumberEditor) jsRows.getEditor()).getTextField().setColumns(TEXTWIDTH);
        ((JSpinner.NumberEditor) jsColumns.getEditor()).getTextField().setColumns(TEXTWIDTH);

    }
    
    protected void createContent(){
    	jspContent = new javax.swing.JScrollPane();
    	table = new javax.swing.JTable();
        table.setModel(tableModel);
        table.setAutoResizeMode(javax.swing.JTable.AUTO_RESIZE_OFF);
        table.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                tableMouseClicked(evt);
            }
        });
        jspContent.setViewportView(table);
    }
    
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {
        jpCenter = new javax.swing.JPanel();
        jpDisplay = new javax.swing.JPanel();
        jlZoom = new javax.swing.JLabel();
        jsZoom = new javax.swing.JSpinner();
        jcbShowLabels = new javax.swing.JCheckBox();
        jcbMDLabels = new javax.swing.JComboBox();
        jcbSortByLabel = new javax.swing.JCheckBox();
        jlGoto = new javax.swing.JLabel();
        jsGoToImage = new javax.swing.JSpinner();        
        
        
        Container container = getContentPane();
        container.setLayout(new GridBagLayout());
        GridBagConstraints c = new GridBagConstraints();
        
        createToolbar();
        c.fill = GridBagConstraints.HORIZONTAL;
        c.gridx = 0; 
        c.gridy = 0;        
        container.add(toolBar, c);


        createContent();
        c.fill = GridBagConstraints.BOTH;
        c.gridx = 0; 
        c.gridy = 1;
        c.weightx = 1.0;
        c.weighty = 1.0;
        container.add(jspContent, c);

//        createBottom();
//        c.fill = GridBagConstraints.HORIZONTAL;
//        c.gridx = 0; 
//        c.gridy = 2;
//        c.weighty = 0.0;
//        container.add(jpBottom, c);        

        //setInitialValues();
    }// </editor-fold>//GEN-END:initComponents
    
    
    private void jsZoomStateChanged(javax.swing.event.ChangeEvent evt) {//GEN-FIRST:event_jsZoomStateChanged
        setZoom((Integer) jsZoom.getValue());
    }//GEN-LAST:event_jsZoomStateChanged
    
    //Handle user request to display item label
    private void jcbShowLabelsActionPerformed(java.awt.event.ActionEvent evt) {
    	tableModel.setShowLabels(jcbShowLabels.isSelected());
        updateTable();
    }//GEN-LAST:event_jcbShowLabelsActionPerformed
    private void formWindowOpened(java.awt.event.WindowEvent evt) {//GEN-FIRST:event_formWindowOpened
        //pack();
//        ImagesWindowFactory.setConvenientSize(this);
//        setInitialValues();
    }//GEN-LAST:event_formWindowOpened
    private void jsRowsStateChanged(javax.swing.event.ChangeEvent evt) {//GEN-FIRST:event_jsRowsStateChanged
        if (!isUpdating) {
            setRowsValue((Integer) jsRows.getValue());
        }
}//GEN-LAST:event_jsRowsStateChanged
    private void jsColumnsStateChanged(javax.swing.event.ChangeEvent evt) {//GEN-FIRST:event_jsColumnsStateChanged
        if (!isUpdating) {
            setColumnsValue((Integer) jsColumns.getValue());
        }
}//GEN-LAST:event_jsColumnsStateChanged
    private void jsGoToImageStateChanged(javax.swing.event.ChangeEvent evt) {//GEN-FIRST:event_jsGoToImageStateChanged
        if (!internalChange)
        	goToImage((Integer) jsGoToImage.getValue() - 1);
        internalChange = false;
}//GEN-LAST:event_jsGoToImageStateChanged
    private void formComponentResized(java.awt.event.ComponentEvent evt) {//GEN-FIRST:event_formComponentResized
    	Dimension dim = evt.getComponent().getSize();
    	DEBUG.printMessage(dim.toString());
    	DEBUG.printMessage(evt.getComponent().getName());
    	if (!isUpdating)
    	{
    		startUpdater();
    	}
    }//GEN-LAST:event_formComponentResized
    private void tableMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_tableMouseClicked
        final Point p = evt.getPoint();
    	int view_row = table.rowAtPoint(p);
        int view_col = table.columnAtPoint(p);

        if (evt.getButton() == MouseEvent.BUTTON1) {  // Left click.
            if (evt.getClickCount() > 1) {
                Object item = table.getValueAt(view_row, view_col);

                if (item instanceof AbstractGalleryImageItem) {
                    ImagesWindowFactory.captureFrame(((AbstractGalleryImageItem) item).getImagePlus());
                }
            } else {
                // Ctrl adds items to selection, otherwise previous ones are removed.
                if (!evt.isControlDown()) {
                    tableModel.clearSelection();
                }

                if (evt.isShiftDown()) {
                    tableModel.selectRange(previousSelectedRow, previousSelectedCol,
                            			view_row, view_col);
                } else {
                    tableModel.setSelected(view_row, view_col, true);
                }             
                internalChange = true;
                jsGoToImage.setValue(tableModel.getDataIndex(view_row, view_col) + 1);
                table.repaint();
            }

            if (!evt.isShiftDown()) {
                previousSelectedRow = view_row;
                previousSelectedCol = view_col;
            }
        } else if (evt.getButton() == MouseEvent.BUTTON3) {  // Right click.
            if (tableModel.getSelectedItems().size() < 2) {
                tableModel.clearSelection();
                tableModel.setSelected(view_row, view_col, true);

                table.setRowSelectionInterval(view_row, view_row);
                table.setColumnSelectionInterval(view_col, view_col);

                table.repaint();
            }

            final MouseEvent me = evt;
            SwingUtilities.invokeLater(new Runnable() {
                public void run() {
                    jpopUpMenuTable.show(me.getComponent(), p);
                }
            });
        }
    }//GEN-LAST:event_tableMouseClicked

    private void jtbNormalizeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jtbNormalizeActionPerformed
        setNormalized(jtbNormalize.isSelected());
        updateTable();
    }//GEN-LAST:event_jtbNormalizeActionPerformed

    
    private void jcbMDLabelsItemStateChanged(java.awt.event.ItemEvent evt) {//GEN-FIRST:event_jcbMDLabelsItemStateChanged
        if (evt.getStateChange() == ItemEvent.DESELECTED) {
            tableModel.setSelectedLabel(jcbMDLabels.getSelectedIndex());
            updateTable();
        }
    }//GEN-LAST:event_jcbMDLabelsItemStateChanged

    private void jcbSortByLabelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jcbSortByLabelActionPerformed
        tableModel.setSorting(jcbSortByLabel.isSelected());
        updateTable();
    }//GEN-LAST:event_jcbSortByLabelActionPerformed

    private void jtbUseGeometryActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jtbUseGeometryActionPerformed
        if (tableModel.containsGeometryInfo()) {
            ((MDTableModel) tableModel).setUseGeometry(jtbUseGeometry.isSelected());

            updateTable();
        }
}//GEN-LAST:event_jtbUseGeometryActionPerformed

    private void jcbAutoAdjustColumnsStateChanged(ActionEvent evt) {//GEN-FIRST:event_jcbAutoAdjustColumnsStateChanged
        setAutoAdjustColumns(jcbAutoAdjustColumns.isSelected());
}//GEN-LAST:event_jcbAutoAdjustColumnsStateChanged
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JLabel jlZoom;
    private javax.swing.JLabel jlGoto;
    private javax.swing.JLabel jlRows;
    private javax.swing.JLabel jlColumns;
    private javax.swing.JToggleButton jcbAutoAdjustColumns;
    private javax.swing.JComboBox jcbMDLabels;
    private javax.swing.JCheckBox jcbShowLabels;
    private javax.swing.JCheckBox jcbSortByLabel;
    private javax.swing.JPanel jpCenter;
    private javax.swing.JPanel jpDisplay;
    protected javax.swing.JPanel jpBottom;
    protected javax.swing.JSpinner jsColumns;
    protected javax.swing.JSpinner jsGoToImage;
    private javax.swing.JScrollPane jspContent;
    protected javax.swing.JSpinner jsRows;
    protected javax.swing.JSpinner jsZoom;
    private javax.swing.JToggleButton jtbNormalize;
    private javax.swing.JToggleButton jtbUseGeometry;
    private javax.swing.JTable table;
    private javax.swing.JToolBar toolBar;
    // End of variables declaration//GEN-END:variables

    class TableUpdater extends TimerTask {

        @Override
        public void run() {
        	tableUpdaterTask = null;
            updateTable();
        }
    }

    class JMenuBarTable extends JMenuBar {

        protected JMenu jmFile = new JMenu(Labels.LABEL_GALLERY_FILE);
        protected JMenu jmSave = new JMenu(Labels.LABEL_GALLERY_SAVE);
        protected JMenuItem jmiSaveAsMetadata = new JMenuItem(Labels.LABEL_GALLERY_SAVE_AS_METADATA);
        protected JMenuItem jmiSaveAsStack = new JMenuItem(Labels.LABEL_GALLERY_SAVE_AS_IMAGE);
        protected JMenuItem jmiSaveSelectionAsMetadata = new JMenuItem(Labels.LABEL_GALLERY_SAVE_SELECTION_AS_METADATA);
        protected JMenuItem jmiSaveSelectionAsStack = new JMenuItem(Labels.LABEL_GALLERY_SAVE_SELECTION_AS_IMAGE);
        protected JMenuItem jmiExit = new JMenuItem(Labels.LABEL_GALLERY_EXIT);
        protected JMenu jmStatistics = new JMenu(Labels.LABEL_MENU_STATISTICS);
        protected JMenuItem jmiAVG = new JMenuItem(Labels.BUTTON_MEAN);
        protected JMenuItem jmiSTDEV = new JMenuItem(Labels.BUTTON_STD_DEVIATION);
        protected JMenuItem jmiPCA = new JMenuItem(Labels.BUTTON_PCA);
        protected JMenuItem jmiFSC = new JMenuItem(Labels.BUTTON_FSC);
        protected JMenu jmOpenAs = new JMenu(Labels.LABEL_MENU_OPEN_AS);
        protected JMenuItem jmiOpenAs3D = new JMenuItem(Labels.OPERATION_OPEN_AS_3D_VOLUME);
        protected JMenuItem jmiOpenAsMetadata = new JMenuItem(Labels.OPERATION_OPEN_AS_METADATA);
        protected JMenuItem jmiOpenAsStack = new JMenuItem(Labels.OPERATION_OPEN_AS_STACK);
        protected JMenu jmReslice = new JMenu(Labels.LABEL_RESLICE);
        protected JMenuItem jmiResliceTop = new JMenuItem(Labels.LABEL_RESLICE_TOP);
        protected JMenuItem jmiResliceRight = new JMenuItem(Labels.LABEL_RESLICE_RIGHT);

        public JMenuBarTable() {
            super();

            jmSave.add(jmiSaveAsMetadata);
            jmSave.add(jmiSaveAsStack);
            jmSave.addSeparator();
            jmSave.add(jmiSaveSelectionAsMetadata);
            jmSave.add(jmiSaveSelectionAsStack);

            add(jmFile);
            jmFile.add(jmSave);
            jmFile.addSeparator();
            jmFile.add(jmiExit);

            jmiSaveAsMetadata.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    saveAsMetadata(true);
                }
            });

            jmiSaveSelectionAsMetadata.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    saveAsMetadata(false);
                }
            });

            jmiSaveAsStack.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    saveAsStack(true);
                }
            });

            jmiSaveSelectionAsStack.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    saveAsStack(false);
                }
            });

            jmiExit.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent ae) {
                    System.exit(0);
                }
            });

            add(jmStatistics);
            jmStatistics.add(jmiAVG);
            jmStatistics.add(jmiSTDEV);
            jmStatistics.add(jmiPCA);
            jmStatistics.add(jmiFSC);

            jmiAVG.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    avgImage();
                }
            });

            jmiSTDEV.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    stdDevImage();
                }
            });

            jmiPCA.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    pca();
                }
            });

            jmiFSC.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    fsc();
                }
            });

            add(jmOpenAs);
            jmOpenAs.add(jmiOpenAs3D);
            jmOpenAs.add(jmiOpenAsMetadata);
            jmOpenAs.add(jmiOpenAsStack);

            jmiOpenAs3D.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    openAs3D();
                }
            });

            jmiOpenAsMetadata.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    ImagesWindowFactory.openFileAsMetadata(tableModel.getFilename());
                }
            });

            jmiOpenAsStack.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    openAsStack();
                }
            });

            add(jmReslice);
            jmReslice.add(jmiResliceTop);
            jmReslice.add(jmiResliceRight);

            jmiResliceTop.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    try {
                        reslice(RESLICE_MODE.TOP_Y);
                    } catch (Exception ex) {
                        DEBUG.printException(ex);
                        IJ.error(ex.getMessage());
                    }
                }
            });

            jmiResliceRight.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    try {
                        reslice(RESLICE_MODE.RIGHT_X);
                    } catch (Exception ex) {
                        DEBUG.printException(ex);
                        IJ.error(ex.getMessage());
                    }
                }
            });

            boolean isVolume = tableModel.isVolume();
            //  boolean isStack = tableModel.isStack();
            boolean isMetaData = tableModel.isMetaData();

            jmStatistics.setEnabled(isMetaData);
            jmReslice.setEnabled(isVolume);
            jmiOpenAs3D.setEnabled(!isMetaData);
            jmiOpenAsMetadata.setEnabled(!isVolume);

            // Volumes can't be saved as metadata.
            jmiSaveAsMetadata.setEnabled(!isVolume);
            jmiSaveSelectionAsMetadata.setEnabled(!isVolume);
        }
    }

    class JPopUpMenuGallery extends JPopupMenu {

        protected Point location;
        protected JMenuItem jmiEnable = new JMenuItem(Labels.LABEL_GALLERY_ENABLE);
        protected JMenuItem jmiDisable = new JMenuItem(Labels.LABEL_GALLERY_DISABLE);
        protected JMenuItem jmiEnableAll = new JMenuItem(Labels.LABEL_GALLERY_ENABLE_ALL);
        protected JMenuItem jmiDisableAll = new JMenuItem(Labels.LABEL_GALLERY_DISABLE_ALL);
        protected JMenuItem jmiEnableFrom = new JMenuItem(Labels.LABEL_GALLERY_ENABLE_FROM);
        protected JMenuItem jmiEnableTo = new JMenuItem(Labels.LABEL_GALLERY_ENABLE_TO);
        protected JMenuItem jmiDisableFrom = new JMenuItem(Labels.LABEL_GALLERY_DISABLE_FROM);
        protected JMenuItem jmiDisableTo = new JMenuItem(Labels.LABEL_GALLERY_DISABLE_TO);

        public JPopUpMenuGallery() {
            add(jmiEnable);
            add(jmiDisable);
            addSeparator();
            add(jmiEnableAll);
            add(jmiDisableAll);
            addSeparator();
            add(jmiEnableFrom);
            add(jmiEnableTo);
            addSeparator();
            add(jmiDisableFrom);
            add(jmiDisableTo);

            jmiEnable.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_E, InputEvent.CTRL_DOWN_MASK));
            jmiDisable.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_D, InputEvent.CTRL_DOWN_MASK));
            jmiEnableAll.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_A, InputEvent.CTRL_DOWN_MASK));
            jmiDisableAll.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_N, InputEvent.CTRL_DOWN_MASK));

//            jmiEnableFrom.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_F, InputEvent.SHIFT_DOWN_MASK));
//            jmiDisableFrom.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_F, InputEvent.CTRL_DOWN_MASK));
//            jmiEnableTo.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_T, InputEvent.SHIFT_DOWN_MASK));
//            jmiDisableTo.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_T, InputEvent.CTRL_DOWN_MASK));

            table.addKeyListener(new KeyListener() {

                public void keyTyped(KeyEvent e) {
                }

                public void keyPressed(KeyEvent e) {
                }

                public void keyReleased(KeyEvent e) {
                    if (e.isControlDown()) {
                        if (e.getKeyCode() == KeyEvent.VK_E) {
                            tableModel.enableSelectedItems();
                        }
                        if (e.getKeyCode() == KeyEvent.VK_D) {
                            tableModel.disableSelectedItems();
                        }
                        if (e.getKeyCode() == KeyEvent.VK_A) {
                            tableModel.enableAllItems();
                        }
                        if (e.getKeyCode() == KeyEvent.VK_N) {
                            tableModel.disableAllItems();
                        }
                    }
                }
            });

            jmiEnable.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    tableModel.enableSelectedItems();
                }
            });

            jmiDisable.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    tableModel.disableSelectedItems();
                }
            });

            jmiEnableAll.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    tableModel.enableAllItems();
                }
            });

            jmiDisableAll.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    tableModel.disableAllItems();
                }
            });

            jmiEnableFrom.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    int row = table.rowAtPoint(location);
                    int col = table.columnAtPoint(location);

                    tableModel.setEnabledFrom(row, col, true);
                }
            });

            jmiEnableTo.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    int row = table.rowAtPoint(location);
                    int col = table.columnAtPoint(location);

                    tableModel.setEnabledTo(row, col, true);
                }
            });

            jmiDisableFrom.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    int row = table.rowAtPoint(location);
                    int col = table.columnAtPoint(location);

                    tableModel.setEnabledFrom(row, col, false);
                }
            });

            jmiDisableTo.addActionListener(new ActionListener() {

                public void actionPerformed(ActionEvent e) {
                    int row = table.rowAtPoint(location);
                    int col = table.columnAtPoint(location);

                    tableModel.setEnabledTo(row, col, false);
                }
            });
        }

        public void show(Component cmpnt, Point location) {
            this.location = location;

            // Update menu items status depending on item.
            int row = table.rowAtPoint(location);
            int col = table.columnAtPoint(location);
            boolean enabled = ((AbstractGalleryImageItem) table.getValueAt(row, col)).isEnabled();

            jmiDisable.setEnabled(enabled);
            jmiEnable.setEnabled(!enabled);

            show(cmpnt, location.x, location.y);
        }
    }

	@Override
	public void mouseClicked(MouseEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mouseEntered(MouseEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mouseExited(MouseEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void mousePressed(MouseEvent arg0) {
		// TODO Auto-generated method stub
		
	}
	
	@Override	
    public void mouseReleased(MouseEvent e) {
        DEBUG.printMessage("Mouse released (# of clicks: " + e.getClickCount() + ")");
    }
	

}
